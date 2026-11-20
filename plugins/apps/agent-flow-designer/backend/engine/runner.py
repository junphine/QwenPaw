# -*- coding: utf-8 -*-
"""Graph execution runner.

Traversal is a *fan-in barrier scheduler*: every edge delivers exactly one
token (live or dead) from its source node, and a node becomes executable only
once all of its in-edges have delivered. This gives deterministic semantics for
the three shapes a workflow graph is made of:

* **Diamond / join** — a merge node waits for *all* of its predecessors instead
  of firing on whichever branch dequeued first.
* **Branch isolation** — edges a router did not select deliver dead tokens, so
  nodes that only receive dead tokens are recorded as ``skipped`` rather than
  silently executed with stale inputs.
* **Failure propagation** — a failed node follows its ``onError`` policy
  (``abort`` | ``continue`` | ``branch``) instead of always running downstream.

Two entry points share this traversal:
  * :func:`run_workflow_sync` — collapses the event stream into the legacy JSON
    contract used by ``/execute`` and ``/run``.
  * ``WorkflowRunner.run()`` — yields raw events, consumed by the SSE path.
"""

from __future__ import annotations

import asyncio
import uuid
from datetime import datetime, timezone
from typing import Any, AsyncIterator, Callable, Dict, List, Optional, Tuple

from .events import EventType, RunEvent
from .log_context import execution_log_scope
from .paused_db import save_paused_run, take_paused_run
from .recorder import RunMeta, RunRecorder
from .registry import NodeRunContext, get_handler
from .retry import RETRY_ENABLED_TYPES, RetryPolicy, backoff_delay, parse_retry_policy
from .state import ExecutionState

#: Reserved ``sourceHandle`` for the error branch of a node (``onError=branch``).
ERROR_HANDLE = "error"

#: Default failure policy. A failed node stops the run instead of letting
#: downstream nodes consume missing output and report a bogus "completed".
DEFAULT_ON_ERROR = "abort"

#: 审批回答白名单。刻意不做模糊匹配：含糊回答不能当成授权。
_APPROVE_ANSWERS = frozenset(
    {"approve", "approved", "yes", "y", "同意", "批准", "通过"}
)


def _parse_approval_answer(answer: Any) -> str:
    """Map a human approval reply to ``"approve"`` or ``"deny"``.

    Anything outside the approve whitelist — including an empty reply — is a
    denial, so an ambiguous answer can never authorise a host tool call.
    """
    text = str(answer or "").strip().lower()
    return "approve" if text in _APPROVE_ANSWERS else "deny"


#: 暂停恢复语义。``answer`` = 人的回复即节点输出（ask 节点）；
#: ``requeue`` = 节点拿到授权后必须真跑一次（工具审批）。
RESUME_MODE_ANSWER = "answer"
RESUME_MODE_REQUEUE = "requeue"
_RESUME_MODES = frozenset({RESUME_MODE_ANSWER, RESUME_MODE_REQUEUE})

#: 只用于 trace 标签，不参与分派，故不收敛成白名单。
PAUSE_KIND_ASK = "ask"
PAUSE_KIND_TOOL_APPROVAL = "tool_approval"


def _normalize_resume_mode(value: Any) -> str:
    """Fail closed to ``answer``.

    A malformed mode must never fall through into the requeue branch, and a
    present-but-null value must not survive as ``None``: the dispatch in
    ``prepare_resume`` compares against these literals, and a silent mismatch
    would mark an approval-gated node completed without ever running it.
    """
    mode = str(value or "").strip()
    return mode if mode in _RESUME_MODES else RESUME_MODE_ANSWER


def _utc_now() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


def _skipped_trace(node: dict, node_id: str, reason: str) -> dict:
    """Build a trace item for a node that was never executed."""
    return {
        "nodeId": node_id,
        "nodeLabel": node.get("label", node_id),
        "type": node.get("type", ""),
        "status": "skipped",
        "timestamp": _utc_now(),
        "durationMs": 0,
        "message": reason,
    }


def _save_paused_run(execution_id: str, workflow: Dict[str, Any], state: ExecutionState) -> None:
    save_paused_run(
        execution_id=execution_id,
        workflow_id=state.workflow_id,
        workflow=workflow,
        state=state.to_json(),
    )


class _Scheduler:
    """In-edge token barrier over the graph's adjacency lists."""

    def __init__(
        self,
        adjacency: Dict[str, List[dict]],
        reverse: Dict[str, List[dict]],
        node_ids: List[str],
    ):
        self.adjacency = adjacency
        self._expected = {nid: len(reverse.get(nid, [])) for nid in node_ids}
        self.received: Dict[str, List[bool]] = {}
        self.live_preds: Dict[str, List[str]] = {}
        self.ready: List[str] = []
        self.executed: set = set()

    def seed(self, node_id: str) -> None:
        """Mark an entry node ready without waiting on its in-edges."""
        self._expected[node_id] = 0
        self.ready.append(node_id)

    def deliver(self, source: str, target: str, live: bool) -> None:
        """Record one edge token; make ``target`` ready once all in-edges arrive."""
        if target in self.executed:
            # A cycle closes back onto a node that already ran; its barrier was
            # computed without this edge, so the token is simply dropped.
            return
        seen = self.received.setdefault(target, [])
        seen.append(live)
        if live:
            self.live_preds.setdefault(target, []).append(source)
        if len(seen) >= self._expected.get(target, 0):
            self.ready.append(target)

    def snapshot(self) -> Dict[str, Any]:
        return {
            "ready": list(self.ready),
            "received": {k: list(v) for k, v in self.received.items()},
            "livePreds": {k: list(v) for k, v in self.live_preds.items()},
            "executed": sorted(self.executed),
        }

    def restore(self, data: Dict[str, Any]) -> None:
        self.ready = list(data.get("ready", []))
        self.received = {
            k: list(v) for k, v in (data.get("received") or {}).items()
        }
        self.live_preds = {
            k: list(v) for k, v in (data.get("livePreds") or {}).items()
        }
        self.executed = set(data.get("executed", []))


def prepare_resume(
    execution_id: str,
    answer: str,
    services: Optional[Dict[str, Any]] = None,
    *,
    meta: Optional[RunMeta] = None,
) -> Optional[Tuple[ExecutionState, "WorkflowRunner"]]:
    """Validate a resume request and rebuild the traversal position.

    Two pause kinds land here, discriminated by ``pending_pause['resumeMode']``:
    ``"answer"`` (the ask node's reply *is* its output — the only behaviour that
    existed before tool approval) and ``"requeue"`` (a tool node paused awaiting
    a governance approval; the node itself must still run, so the reply is filed
    as a one-shot marker in ``state.context`` and the node is re-queued).
    ``services`` is re-resolved by the caller: the handles behind a paused run
    died with the process that paused it.
    ``meta`` re-opens the run's history row on the rebuilt state; without it the
    continuation runs unrecorded, exactly as ``run_workflow_sync`` behaves.
    Returns ``None`` when the paused execution is unknown or expired.
    """
    entry = take_paused_run(execution_id)
    if not entry:
        return None
    workflow = entry["workflow"]
    state = ExecutionState.from_json(entry["state"])
    recorder = RunRecorder(state, state.workflow_id, meta) if meta is not None else None
    runner = WorkflowRunner(
        workflow, state, services=services, recorder=recorder
    )
    pause = state.pending_pause or {}
    node_id = pause.get("nodeId", "")
    # 读侧缺省是向后兼容的唯一支点：早于 resumeMode 落库的暂停快照没有这个键。
    resume_mode = pause.get("resumeMode", RESUME_MODE_ANSWER)
    is_requeue = resume_mode == RESUME_MODE_REQUEUE and node_id

    if is_requeue:
        state.context[f"node_{node_id}_approval"] = _parse_approval_answer(answer)
    elif node_id:
        node_obj = runner.node_map.get(node_id, {})
        state.node_outputs[node_id] = answer
        state.context[f"node_{node_id}_output"] = answer
        state.node_status[node_id] = "completed"
        state.trace_items.append(
            {
                "nodeId": node_id,
                "nodeLabel": node_obj.get("label", node_id),
                "type": pause.get("pauseKind", PAUSE_KIND_ASK) or PAUSE_KIND_ASK,
                "status": "completed",
                "timestamp": _utc_now(),
                "durationMs": 0,
                "inputs": {"question": pause.get("question", "")},
                "output": answer[:500] if isinstance(answer, str) else str(answer)[:500],
                "message": "人工回复已收到，继续执行",
            }
        )

    scheduler_data = pause.get("scheduler") or {}
    if scheduler_data:
        runner.restore_scheduler(scheduler_data)
    else:  # records written before the barrier scheduler existed
        runner.seed_from(list(pause.get("queue", [])), list(pause.get("visited", [])))
    if node_id:
        if is_requeue:
            runner.requeue_node(node_id)
        else:
            runner.mark_resumed(node_id)

    state.pending_pause = None
    state.status = "running"
    return state, runner


async def resume_workflow_sync(
    execution_id: str,
    answer: str,
    services: Optional[Dict[str, Any]] = None,
    *,
    meta: Optional[RunMeta] = None,
) -> Dict[str, Any]:
    """Continue a paused execution with the human answer (legacy contract)."""
    prepared = prepare_resume(execution_id, answer, services, meta=meta)
    if prepared is None:
        return {
            "success": False,
            "detail": f"暂停中的执行不存在或已过期: {execution_id}",
        }
    state, runner = prepared
    return await _consume_run(runner, state)


async def _default_handler(ctx: NodeRunContext) -> AsyncIterator[RunEvent]:
    """Fallback for unknown / unregistered node types.

    Types such as a future ``join`` fall here until a real handler is
    registered; traversal simply follows the node's outgoing edges.
    """
    return
    yield  # pragma: no cover  (makes this an (empty) async generator)


def assemble_final_result(node_outputs: Dict[str, Any], node_map: Dict[str, dict]) -> str:
    """Build the final result text from accumulated node outputs.

    Prefers the last agent output, otherwise concatenates other node outputs.
    """
    agent_outputs: List[str] = []
    other_outputs: List[str] = []

    for nid, nout in node_outputs.items():
        node_obj = node_map.get(nid, {})
        if isinstance(nout, dict) and "selected_branch" in nout:
            other_outputs.append(
                f"[{node_obj.get('label', nid)}]\n"
                f"路由结果: {nout.get('branch_name', '')} "
                f"({nout.get('routeType', '')})"
            )
        elif nout and isinstance(nout, str) and nout.strip():
            if node_obj.get("type") == "agent":
                agent_outputs.append(nout)
            else:
                other_outputs.append(f"[{node_obj.get('label', nid)}]\n{nout}")

    if agent_outputs:
        return agent_outputs[-1].strip()
    if other_outputs:
        return "\n\n".join(other_outputs).strip()
    return "工作流执行完成（无节点输出）。"


class WorkflowRunner:
    """Event-driven traversal over a workflow graph."""

    def __init__(
        self,
        workflow: Dict[str, Any],
        state: ExecutionState,
        cancel_check: Optional[Callable[[], bool]] = None,
        services: Optional[Dict[str, Any]] = None,
        recorder: Optional[RunRecorder] = None,
    ):
        self.workflow = workflow
        self.state = state
        #: Polled between nodes; a run cannot interrupt an in-flight node, it
        #: stops before the next one starts.
        self.cancel_check = cancel_check
        #: Live host handles for tool nodes — never serialised (see
        #: ``NodeRunContext.services``).
        self.services: Dict[str, Any] = services or {}
        #: History writer, or ``None`` to run without recording anything.
        self.recorder = recorder
        self.nodes: List[dict] = workflow.get("nodes", []) or []
        self.edges: List[dict] = workflow.get("edges", []) or []
        self.node_map: Dict[str, dict] = {n["id"]: n for n in self.nodes if "id" in n}
        self.adjacency: Dict[str, List[dict]] = {}
        raw_reverse: Dict[str, List[dict]] = {}
        for edge in self.edges:
            src = edge.get("source")
            tgt = edge.get("target")
            if not src or not tgt or tgt not in self.node_map:
                continue
            self.adjacency.setdefault(src, []).append(
                {"target": tgt, "sourceHandle": edge.get("sourceHandle")}
            )
            raw_reverse.setdefault(tgt, []).append(
                {"source": src, "sourceHandle": edge.get("sourceHandle")}
            )
        self.back_edges = self._find_back_edges(raw_reverse)
        self.reverse: Dict[str, List[dict]] = {}
        for tgt, ins in raw_reverse.items():
            kept = [e for e in ins if (e["source"], tgt) not in self.back_edges]
            if kept:
                self.reverse[tgt] = kept
        self._sched: Optional[_Scheduler] = None
        self._resume_from: str = ""
        self.resumed = False

    def _find_back_edges(self, raw_reverse: Dict[str, List[dict]]) -> set:
        """Classify the edges that close a cycle, iteratively (no recursion).

        The barrier ignores them: their target must already have run for the
        cycle to be reachable, so requiring a token from them would wait forever.
        """
        white, gray = 0, 1
        color = {nid: white for nid in self.node_map}
        found = set()
        roots = list(
            dict.fromkeys(
                [n["id"] for n in self.nodes if n.get("type") == "start"]
                + [nid for nid in self.node_map if not raw_reverse.get(nid)]
                + list(self.node_map)
            )
        )
        for root in roots:
            if color[root] != white:
                continue
            color[root] = gray
            stack = [(root, 0)]
            while stack:
                nid, idx = stack[-1]
                outgoing = self.adjacency.get(nid, [])
                if idx < len(outgoing):
                    stack[-1] = (nid, idx + 1)
                    tgt = outgoing[idx]["target"]
                    if color[tgt] == gray:
                        found.add((nid, tgt))
                    elif color[tgt] == white:
                        color[tgt] = gray
                        stack.append((tgt, 0))
                else:
                    color[nid] = 2  # black: fully explored
                    stack.pop()
        return found

    def start_nodes(self) -> List[dict]:
        return [n for n in self.nodes if n.get("type") == "start"]

    # ── Scheduler plumbing (also used by the HITL resume path) ──────

    def _new_scheduler(self) -> _Scheduler:
        return _Scheduler(self.adjacency, self.reverse, list(self.node_map))

    def restore_scheduler(self, data: Dict[str, Any]) -> None:
        sched = self._new_scheduler()
        sched.restore(data)
        self._sched = sched
        self.resumed = True

    def seed_from(self, queue: List[str], visited: List[str]) -> None:
        """Rebuild a scheduler from a pre-barrier (legacy) pause record."""
        sched = self._new_scheduler()
        sched.executed = set(visited)
        for nid in queue:
            if nid in self.node_map:
                sched.received.setdefault(nid, []).append(True)
                sched.ready.append(nid)
        self._sched = sched
        self.resumed = True

    def mark_resumed(self, node_id: str) -> None:
        """Remember the ask node whose outgoing edges must be delivered on resume."""
        self._resume_from = node_id
        if self._sched is None:
            self._sched = self._new_scheduler()
            self._sched.executed.add(node_id)
        self.resumed = True

    def requeue_node(self, node_id: str) -> None:
        """Put an approval-paused node back in the queue so it really runs.

        Unlike the ask node, this node produced no output: the human reply only
        grants permission. Its in-edge tokens were already delivered before it
        started, so only the executed mark needs clearing — the barrier is
        intact.
        """
        if self._sched is None:
            self._sched = self._new_scheduler()
        self._sched.executed.discard(node_id)
        self._sched.ready.append(node_id)
        self.resumed = True

    async def run(self) -> AsyncIterator[RunEvent]:
        """Yield the traversal's events, recording them as they happen.

        The recording is bracketed here rather than in a generator wrapped around
        the traversal: closing an async generator does not close the generators
        it iterates, so only a ``finally`` in the generator the caller actually
        closes runs when an SSE consumer goes away. That ``finally`` is what turns
        a vanished client into an ``abandoned`` history row instead of a run that
        reports ``running`` forever.

        This is also where the run binds its ``execution_id`` to the log context:
        every path — designer trial, published execution, external ``/run``, HITL
        resume — drives the traversal through here, so tagging once here tags
        the node handlers, the router and the recorder alike.
        """
        with execution_log_scope(self.state.execution_id):
            traversal = self._traverse()
            if self.recorder is None:
                async for event in traversal:
                    yield event
                return

            self.recorder.begin()
            try:
                async for event in traversal:
                    self.recorder.observe()
                    yield event
            except Exception as exc:  # noqa: BLE001
                # Record the outcome before the bracket closes: the callers' own
                # catch-all runs after ``finish``, so without this a node handler
                # that raises is stored as an abandoned run instead of a failed one.
                # ``GeneratorExit`` is a BaseException and deliberately does not land
                # here — a consumer that went away really is an abandoned run.
                self.state.status = "failed"
                self.state.error = str(exc)
                raise
            finally:
                self.recorder.finish()

    async def _traverse(self) -> AsyncIterator[RunEvent]:
        """Traverse the graph and yield node/route/workflow events.

        A scheduler restored by :func:`prepare_resume` continues from the
        paused position; otherwise traversal starts from the start node.
        """
        if self._sched is None:
            starts = self.start_nodes()
            if not starts:
                return
            self._sched = self._new_scheduler()
            self._sched.seed(starts[0]["id"])

        sched = self._sched
        yield RunEvent(
            EventType.WF_START,
            payload={"workflowId": self.state.workflow_id, "resumed": self.resumed},
        )

        if self._resume_from:
            for edge in self.adjacency.get(self._resume_from, []):
                sched.deliver(self._resume_from, edge["target"], live=True)
            self._resume_from = ""

        while sched.ready:
            if self.cancel_check and self.cancel_check():
                async for event in self._abort(
                    "",
                    "",
                    status="cancelled",
                    reason="执行已被取消",
                    skip_reason="执行已取消，节点未运行",
                ):
                    yield event
                return

            node_id = sched.ready.pop(0)
            if node_id in sched.executed:
                continue
            node = self.node_map.get(node_id)
            if not node:
                sched.executed.add(node_id)
                continue
            sched.executed.add(node_id)

            tokens = sched.received.get(node_id, [])
            if tokens and not any(tokens):
                # Every in-edge was pruned by a router or an aborted path.
                self.state.node_status[node_id] = "skipped"
                # disable@byron
                #trace = _skipped_trace(node, node_id, "上游分支未命中，节点已跳过")
                # self.state.trace_items.append(trace)
                # yield RunEvent(EventType.NODE_DONE, node_id, {"trace": trace})
                for edge in self.adjacency.get(node_id, []):
                    sched.deliver(node_id, edge["target"], live=False)
                continue

            node_type = node.get("type", "")
            handler = get_handler(node_type) or _default_handler
            route_info: Optional[Dict[str, Any]] = None
            failed_detail = ""

            ctx = NodeRunContext(
                node=node,
                state=self.state,
                workflow=self.workflow,
                live_predecessors=list(sched.live_preds.get(node_id, [])),
                services=self.services,
            )
            self.state.node_status[node_id] = "running"

            yield RunEvent(
                EventType.NODE_START,
                node_id,
                {"nodeLabel": node.get("label", node_id), "type": node_type},
            )

            if node_type in RETRY_ENABLED_TYPES:
                policy = parse_retry_policy(node.get("config"))
            else:
                policy = RetryPolicy()
            # 审批恢复执行：标记存在则本次只跑一次，绝不重新弹窗问人，也绝不
            # 在没有新授权的情况下重跑审批工具。runner 只读存在性、绝不回填；
            # handler 照样 pop（consume-once 仅一处）。timeout 与重试正交，保留。
            if self.state.context.get(f"node_{node_id}_approval") is not None:
                policy = policy.with_retries_disabled()

            for attempt in range(policy.max_retries + 1):
                outcome: Dict[str, Any] = {"kind": "none"}
                stream_live = attempt == policy.max_retries
                async for event in self._run_one_attempt(
                    handler, ctx, policy, stream_live, outcome
                ):
                    if event.trace_item is not None:
                        trace = event.trace_item
                        if policy.max_retries > 0 and event.type in (
                            EventType.NODE_DONE, EventType.NODE_ERROR
                        ):
                            trace = {**trace, "attempts": attempt + 1}
                        self.state.trace_items.append(trace)
                    if event.type == EventType.ROUTE:
                        route_info = event.payload
                    if event.type in (EventType.NODE_DONE, EventType.NODE_ERROR):
                        self.state.node_status[node_id] = (
                            "failed" if event.type == EventType.NODE_ERROR else "completed"
                        )
                    if event.type == EventType.NODE_ERROR:
                        failed_detail = str(
                            (event.trace_item or {}).get("error", "")
                            or (event.trace_item or {}).get("message", "节点执行失败")
                        )
                    if event.type == EventType.WF_DONE:
                        self.state.result = event.payload.get("result", "") or ""
                        self.state.reached_end = True
                        # A sibling branch still queued (or never delivered) when this
                        # End node fired must not vanish from the run: the graph passes
                        # validation, so dropping it silently would report "completed"
                        # for work that never happened.
                        async for skipped in self._skip_unexecuted(
                            "工作流已到达结束节点，节点未运行"
                        ):
                            yield skipped
                        self.state.status = "completed"
                        yield event
                        return
                    if event.type == EventType.WF_PAUSE:
                        self.state.status = "paused"
                        self.state.pending_pause = {
                            "nodeId": node_id,
                            "question": event.payload.get("question", ""),
                            # 写侧就归一化：分派读的是这两个字面量，非法值必须 fail-closed
                            # 到 answer（= 最保守的旧语义），不能原样落库。
                            "resumeMode": _normalize_resume_mode(
                                event.payload.get("resumeMode")
                            ),
                            "pauseKind": str(
                                event.payload.get("pauseKind") or PAUSE_KIND_ASK
                            ).strip(),
                            "scheduler": sched.snapshot(),
                            # Legacy fields, kept so older readers still find a position.
                            "queue": list(sched.ready),
                            "visited": sorted(sched.executed),
                        }
                        _save_paused_run(self.state.execution_id, self.workflow, self.state)
                        yield event
                        return
                    yield event

                if outcome["kind"] == "error" and attempt < policy.max_retries:
                    await asyncio.sleep(backoff_delay(policy, attempt + 1))
                    continue
                break

            decisions = self._classify_outgoing(node, route_info, bool(failed_detail))
            if decisions is None:
                async for abort_event in self._abort(node_id, failed_detail):
                    yield abort_event
                return

            for edge, live in zip(self.adjacency.get(node_id, []), decisions):
                sched.deliver(node_id, edge["target"], live=live)

        # Falling out of the loop means the queue drained: no end node was
        # reached, nothing failed, nothing paused. The run is over and its
        # status has to say so — every early exit above already recorded its
        # own outcome, and the history recorder reads this field as the result.
        self.state.status = "completed"

    async def _run_one_attempt(
        self,
        handler: Callable[[NodeRunContext], AsyncIterator[RunEvent]],
        ctx: NodeRunContext,
        policy: RetryPolicy,
        stream_live: bool,
        outcome: Dict[str, Any],
    ) -> AsyncIterator[RunEvent]:
        """Consume one handler invocation, buffering or streaming its events.

        ``stream_live`` is True only on the final attempt (or a default
        single-shot node), so a failed-and-retried attempt never leaks tokens or
        an error trace to the consumer. ``outcome['kind']`` tells the attempt
        loop whether to retry.
        """
        gen = handler(ctx)
        pending: List[RunEvent] = []
        try:
            async with asyncio.timeout(policy.node_timeout_sec):
                async for event in gen:
                    etype = event.type
                    if etype == EventType.NODE_DONE:
                        outcome["kind"] = "done"
                    elif etype == EventType.NODE_ERROR:
                        outcome["kind"] = "error"

                    if stream_live:
                        yield event
                        continue

                    pending.append(event)
                    if etype in (EventType.NODE_DONE, EventType.WF_DONE, EventType.WF_PAUSE):
                        for buffered in pending:
                            yield buffered
                        return
                    if etype == EventType.NODE_ERROR:
                        return
                for buffered in pending:
                    yield buffered
        except TimeoutError:
            trace = {
                "nodeId": ctx.node_id,
                "nodeLabel": ctx.node.get("label", ctx.node_id),
                "type": ctx.node_type,
                "status": "failed",
                "timestamp": "",
                "durationMs": 0,
                "error": f"节点执行超时 ({policy.node_timeout_sec:g}s)",
                "message": "节点执行超时",
            }
            outcome["kind"] = "error"
            if stream_live:
                yield RunEvent(EventType.NODE_ERROR, ctx.node_id, {"trace": trace})
        finally:
            await gen.aclose()

    # ── Failure / branch dispatch ───────────────────────────────────

    def _classify_outgoing(
        self, node: dict, route_info: Optional[Dict[str, Any]], failed: bool
    ) -> Optional[List[bool]]:
        """Return one live flag per outgoing edge, or ``None`` to abort the run."""
        edges = self.adjacency.get(node.get("id", ""), [])
        if failed:
            policy = (node.get("config") or {}).get("onError") or DEFAULT_ON_ERROR
            if policy == "continue":
                return [True] * len(edges)
            if policy == "branch":
                if any(e.get("sourceHandle") == ERROR_HANDLE for e in edges):
                    return [e.get("sourceHandle") == ERROR_HANDLE for e in edges]
            return None

        if route_info is not None:
            branch_id = route_info.get("branchId")
            matched = route_info.get("matched")
            return [
                bool(branch_id and e.get("sourceHandle") == branch_id)
                or (not e.get("sourceHandle") and bool(matched))
                for e in edges
            ]

        return [e.get("sourceHandle") != ERROR_HANDLE for e in edges]

    async def _skip_unexecuted(self, skip_reason: str) -> AsyncIterator[RunEvent]:
        """Record every node the traversal will not run, and announce each one.

        Shared by the two ways a run can stop early — an aborted/cancelled traversal
        and a branch reaching its End node — so neither can leave a node absent from
        ``node_status`` and the trace. Callers must drain this before their terminal
        event: consumers stop reading the node stream at ``WF_DONE``/``WF_ERROR``.
        """
        for nid, node in self.node_map.items():
            if nid in self._sched.executed:
                continue
            self.state.node_status[nid] = "skipped"
            trace = _skipped_trace(node, nid, skip_reason)
            self.state.trace_items.append(trace)
            yield RunEvent(EventType.NODE_DONE, nid, {"trace": trace})

    async def _abort(
        self,
        node_id: str,
        detail: str,
        *,
        status: str = "failed",
        reason: str = "",
        skip_reason: str = "因上游失败而未执行",
    ) -> AsyncIterator[RunEvent]:
        """Stop the run, recording every unexecuted node as skipped."""
        reason = reason or f"节点 {node_id} 执行失败，onError=abort：已中止执行"
        async for event in self._skip_unexecuted(skip_reason):
            yield event

        self.state.status = status
        self.state.error = detail or reason
        payload: Dict[str, Any] = {"detail": detail or reason}
        if status == "cancelled":
            payload["cancelled"] = True
        else:
            payload["failedNodeId"] = node_id
        yield RunEvent(EventType.WF_ERROR, node_id, payload)


async def _consume_run(
    runner: "WorkflowRunner",
    state: ExecutionState,
) -> Dict[str, Any]:
    """Drive a full traversal and collapse the events into the legacy contract.

    Shared by the fresh (``run_workflow_sync``) and HITL (``resume_workflow_sync``)
    synchronous paths so both produce byte-identical responses.
    """
    execution_id = state.execution_id
    workflow_id = state.workflow_id
    try:
        async for _ in runner.run():
            pass

        if state.status == "paused" and state.pending_pause:
            question = state.pending_pause.get("question", "") or ""
            return {
                "success": True,
                "data": {
                    "execution_id": execution_id,
                    "status": "paused",
                    "result": question,
                    "pause": {
                        "node_id": state.pending_pause.get("nodeId", ""),
                        "question": question,
                    },
                    "trace": {
                        "workflowId": workflow_id,
                        "status": "paused",
                        "items": state.trace_items,
                    },
                },
            }

        if state.status in ("failed", "cancelled"):
            outcome = "cancelled" if state.status == "cancelled" else "failed"
            return {
                "success": False,
                "detail": state.error,
                "data": {
                    "execution_id": execution_id,
                    "status": outcome,
                    "result": (
                        "执行已取消" if outcome == "cancelled" else f"执行失败: {state.error}"
                    ),
                    "trace": {
                        "workflowId": workflow_id,
                        "status": outcome,
                        "items": state.trace_items,
                    },
                },
            }

        if not state.reached_end:
            state.result = assemble_final_result(state.node_outputs, runner.node_map)

        return {
            "success": True,
            "data": {
                "execution_id": execution_id,
                "status": "completed",
                "result": state.result.strip(),
                "trace": {
                    "workflowId": workflow_id,
                    "status": "completed",
                    "items": state.trace_items,
                },
            },
        }
    except Exception as exc:  # noqa: BLE001  (mirror original catch-all)
        state.status = "failed"
        state.error = str(exc)
        return {
            "success": False,
            "detail": f"执行工作流时发生错误: {str(exc)}",
            "data": {
                "execution_id": execution_id,
                "status": "failed",
                "result": f"执行失败: {str(exc)}",
                "trace": {
                    "workflowId": workflow_id,
                    "status": "failed",
                    "items": state.trace_items,
                },
            },
        }


async def run_workflow_sync(
    workflow_id: str,
    workflow: Dict[str, Any],
    context: Dict[str, Any],
    services: Optional[Dict[str, Any]] = None,
    *,
    meta: Optional[RunMeta] = None,
) -> Dict[str, Any]:
    """Execute a workflow and return the legacy JSON contract.

    ``meta`` is what the API layer knows and the run cannot derive — its owner,
    how it was triggered, the caller's input. Without it nothing is written:
    history is opt-in per call site, so an unauthenticated or otherwise
    unattributable run never lands in someone's list.
    """
    execution_id = str(uuid.uuid4())
    state = ExecutionState(
        execution_id=execution_id,
        workflow_id=workflow_id,
        context=dict(context),
    )
    recorder = RunRecorder(state, workflow_id, meta) if meta is not None else None
    runner = WorkflowRunner(workflow, state, services=services, recorder=recorder)

    if not runner.start_nodes():
        result_text = "工作流执行完成（无开始节点）。"
        if recorder is not None:
            # There is no traversal to bracket, so the outcome is stated on the
            # state first: a run the recorder leaves as ``running`` is by
            # definition one that stopped without an outcome, and this did not.
            state.status = "completed"
            state.result = result_text
            recorder.begin()
            recorder.finish()
        return {
            "success": True,
            "data": {
                "execution_id": execution_id,
                "status": "completed",
                "result": result_text,
                "trace": {"workflowId": workflow_id, "status": "completed", "items": []},
            },
        }

    return await _consume_run(runner, state)
