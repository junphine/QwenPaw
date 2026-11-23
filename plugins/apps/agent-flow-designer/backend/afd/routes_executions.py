# -*- coding: utf-8 -*-
"""Execution / streaming / HITL / history routes and the execution core.

The 8 route functions live at module level (tests call them directly);
``register_routes`` applies the original decorators programmatically in
BASE main.py order, so FastAPI registration order is unchanged. The
in-flight-run registry (``_ACTIVE_RUNS``) has single ownership here.
"""

import asyncio
import json
import uuid
from typing import Any, Dict, NamedTuple, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from qwenpaw.pawapp import PawAppContext, get_scoped_ctx

from engine import (
    EventType,
    ExecutionState,
    WorkflowRunner,
    assemble_final_result,
    prepare_resume,
    resume_workflow_sync,
    run_workflow_sync,
)
from engine.recorder import RunMeta, RunRecorder
from engine.run_db import (
    RUN_STATUSES as _RUN_STATUSES,
    get_run as _get_run,
    list_nodes as _list_run_nodes,
    list_runs as _list_runs,
)

from .models import CancelRequest, ExecuteRequest, ResumeRequest
from .store import (
    _LOCK, _VERSIONS_FILE, _find_workflow, _load_versions, _load_from_disk,
    _require_owner, _require_paused_owner,
)
from .tools import _build_tool_services


def _run_meta(
    workflow: Dict[str, Any],
    context: Dict[str, Any],
    user_id: str,
    trigger_kind: str,
) -> RunMeta:
    """Attribution the engine cannot derive about a run that is about to start.

    ``owner_user_id`` is the authenticated principal: history rows are scoped by
    it on every read, so a run recorded under the wrong owner is invisible to
    the person who ran it and readable by someone else. ``workflow_version`` is
    only ever present for a run on a published snapshot.
    """
    return RunMeta(
        owner_user_id=user_id or "default",
        trigger_kind=trigger_kind,
        workflow_version=workflow.get("deployed_version_number"),
        source_text=str(context.get("user_input") or ""),
    )


# ── In-flight runs (cancellation) ───────────────────────────────────
class _ActiveRun(NamedTuple):
    """What one streaming run leaves behind for the cancel endpoint to find.

    ``workflow_id`` is part of the identity, not decoration: a cancel request is
    addressed at ``/workflows/{id}/executions/{execution_id}/cancel``, and a run
    found under a workflow it never belonged to must read as absent — the same
    answer the history read API gives.
    """

    stop: asyncio.Event
    owner: str
    workflow_id: str


#: Only a streaming run is registered: a synchronous request blocks until the
#: end and never learns its own id first.
_ACTIVE_RUNS: Dict[str, _ActiveRun] = {}


def _begin_run(execution_id: str, user_id: str, workflow_id: str) -> asyncio.Event:
    """Register an in-flight run and return the flag that stops it."""
    stop = asyncio.Event()
    _ACTIVE_RUNS[execution_id] = _ActiveRun(stop, user_id, workflow_id)
    return stop


def _end_run(execution_id: str) -> None:
    _ACTIVE_RUNS.pop(execution_id, None)



def _build_execution_context(
    req: ExecuteRequest, ctx: Optional[PawAppContext] = None
) -> dict:
    """Build the initial execution context from the request + host identity.

    ``SYS_USER_ID`` and ``AGENT_ID`` are read from the authenticated PawApp
    context rather than the request body, so a run cannot adopt another user's
    identity by crafting a payload.
    """
    user_input = req.messages[-1].content if req.messages else ""
    principal = str(getattr(ctx, "user_id", "") or "default")
    return {
        "messages": [m.model_dump() for m in req.messages],
        "user_input": user_input,
        "SYS_USER_ID": principal,
        "USER_UID": req.user_uid or principal,
        "USER_NAME": req.user_name or principal,
        "USER_LANG": req.lang,
        "AGENT_ID": str(getattr(ctx, "agent_id", "") or "default"),
        "CONVERSATION_ID": req.conversation_id,
        "REQUEST_ID": str(uuid.uuid4()),
        "AGENT_USER_MSG": user_input,
    }



async def _resolve_execution_workflow(
    workflow_id: str, preview: bool = False, user_id: str = ""
) -> dict:
    """Load a workflow for execution, honouring deployed-version isolation.

    Shared by the synchronous ``/execute`` endpoint and the streaming
    ``/execute/stream`` endpoint so both resolve the exact same graph. When the
    workflow is deployed and ``preview`` is false, the deployed snapshot is used
    instead of the current editing state. Raises 404 when not found and 403 when
    ``user_id`` is given and the workflow belongs to someone else.
    """
    async with _LOCK(workflow_id):
        workflow = _find_workflow(workflow_id)

        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        if user_id:
            _require_owner(workflow, user_id, "执行")

    # ── Deployed version isolation ──────────────────────────────
    # If deployed and not in preview mode, load the deployed version snapshot
    deployed_version_id = workflow.get("deployed_version_id")
    if deployed_version_id and not preview:
        v = _load_from_disk(_VERSIONS_FILE(workflow_id,deployed_version_id))
        if v and v.get("id") == deployed_version_id:
            # Use the deployed snapshot instead of the editing state
            workflow = {
                "id": workflow_id,
                "name": v.get("name", ""),
                "description": v.get("description", ""),
                "nodes": v.get("nodes", []),
                "edges": v.get("edges", []),
                "system_prompt": v.get("system_prompt", ""),
                "created_at": v.get("created_at", ""),
                "updated_at": v.get("published_at", ""),
                "deployed_version_id": deployed_version_id,
                "deployed_version_number": v.get("version"),
                "deployed_at": workflow.get("deployed_at"),
            }

    return workflow



async def execute_workflow(
    workflow_id: str,
    req: ExecuteRequest,
    preview: bool = False,
    ctx: PawAppContext = Depends(get_scoped_ctx),
) -> dict:
    """Execute a workflow with full node data flow support.

    If the workflow is deployed, the execution uses the deployed version snapshot
    instead of the current editing state, ensuring complete isolation between
    the deployed service and ongoing edits.

    When preview=true, the current editing state is used directly, bypassing
    the deployed version snapshot. This is used by the Preview & Debug panel.

    The authenticated principal behind ``ctx`` supplies the system variables the
    Start node exposes, so a run cannot adopt another user's identity.
    """
    workflow = await _resolve_execution_workflow(workflow_id, preview, ctx.user_id)
    return await _execute_workflow_core(
        workflow_id,
        req,
        workflow,
        ctx,
        trigger_kind="designer" if preview else "deployed_api",
    )



# ── Unified External Execution API ────────────────────────────────

async def run_workflow(
    workflow_id: str,
    req: ExecuteRequest,
    ctx: PawAppContext = Depends(get_scoped_ctx),
) -> dict:
    """Unified external execution endpoint.
    
    Only deployed workflows can be executed via this endpoint.
    Returns 400 if the workflow is not deployed.
    Automatically uses the deployed version snapshot, completely
    isolated from the editing state.
    """
    async with _LOCK(workflow_id):
        workflow = _find_workflow(workflow_id)

        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        _require_owner(workflow, ctx.user_id, "调用")

        # ── Deployment check ───────────────────────────────────────
        deployed_version_id = workflow.get("deployed_version_id")
        if not deployed_version_id:
            raise HTTPException(
                status_code=400,
                detail="Workflow is not deployed. Please deploy before calling this endpoint."
            )
        
        # Load deployed version snapshot
        deployed_version = _load_from_disk(_VERSIONS_FILE(workflow_id,deployed_version_id))
        
        if not deployed_version:
            raise HTTPException(status_code=404, detail="Deployed version not found")
        
        # Use the deployed snapshot
        workflow = {
            "id": workflow_id,
            "name": deployed_version.get("name", ""),
            "description": deployed_version.get("description", ""),
            "nodes": deployed_version.get("nodes", []),
            "edges": deployed_version.get("edges", []),
            "system_prompt": deployed_version.get("system_prompt", ""),
            "created_at": deployed_version.get("created_at", ""),
            "updated_at": deployed_version.get("published_at", ""),
            "deployed_version_id": deployed_version_id,
            "deployed_version_number": deployed_version.get("version"),
            "deployed_at": workflow.get("deployed_at"),
        }
    
    return await _execute_workflow_core(
        workflow_id, req, workflow, ctx, trigger_kind="api"
    )



async def _execute_workflow_core(
    workflow_id: str,
    req: ExecuteRequest,
    workflow: dict,
    ctx: Optional[PawAppContext] = None,
    *,
    trigger_kind: str = "deployed_api",
) -> dict:
    """Execute a workflow via the graph engine (legacy-compatible contract)."""
    context = _build_execution_context(req, ctx)
    services = await _build_tool_services(ctx)
    meta = _run_meta(
        workflow, context, str(getattr(ctx, "user_id", "") or ""), trigger_kind
    )
    return await run_workflow_sync(
        workflow_id, workflow, context, services=services, meta=meta
    )


def _sse(obj: dict) -> str:
    """Serialize one object as an SSE ``data:`` frame."""
    return f"data: {json.dumps(obj, ensure_ascii=False)}\n\n"


async def _stream_events(
    execution_id: str,
    workflow_id: str,
    state: ExecutionState,
    runner: "WorkflowRunner",
):
    """Drive a traversal and yield SSE frames for every engine event.

    Shared by the fresh streaming path and the HITL resume path so both emit
    an identical wire contract:
      wf_start   {executionId, workflowId, resumed}
      node_start {nodeId, nodeLabel, type}
      token      {nodeId, delta}          (agent token-level streaming)
      node       {nodeId, trace}          (trace status completed|failed|skipped)
      route      {nodeId, branchId, matched}
      pause      {executionId, nodeId, question, traceItems}  (HITL)
      wf_done    {executionId, result, traceItems}
      wf_error   {executionId, detail, traceItems}
    """
    if not runner.resumed and not runner.start_nodes():
        yield _sse({"event": "wf_start", "executionId": execution_id, "workflowId": workflow_id, "resumed": False})
        yield _sse({
            "event": "wf_done",
            "executionId": execution_id,
            "result": "工作流执行完成（无开始节点）。",
            "traceItems": [],
        })
        if runner.recorder is not None:
            # Nothing is traversed, so the runner's bracket never opens: the
            # outcome the caller is being handed has to be written explicitly.
            state.status = "completed"
            state.result = "工作流执行完成（无开始节点）。"
            runner.recorder.begin()
            runner.recorder.finish()
        return

    yield _sse({"event": "wf_start", "executionId": execution_id, "workflowId": workflow_id, "resumed": runner.resumed})
    try:
        async for event in runner.run():
            if event.type == EventType.NODE_START:
                yield _sse({
                    "event": "node_start",
                    "nodeId": event.node_id,
                    "nodeLabel": event.payload.get("nodeLabel", event.node_id),
                    "type": event.payload.get("type", ""),
                })
            elif event.type == EventType.NODE_TOKEN:
                yield _sse({
                    "event": "token",
                    "nodeId": event.node_id,
                    "delta": event.payload.get("delta", ""),
                })
            elif event.type in (EventType.NODE_DONE, EventType.NODE_ERROR):
                trace = event.trace_item or {}
                yield _sse({
                    "event": "node",
                    "nodeId": event.node_id,
                    "status": trace.get("status", "completed"),
                    "trace": trace,
                })
            elif event.type == EventType.ROUTE:
                yield _sse({
                    "event": "route",
                    "nodeId": event.node_id,
                    "branchId": event.payload.get("branchId", ""),
                    "matched": event.payload.get("matched", False),
                })
            elif event.type == EventType.WF_PAUSE:
                yield _sse({
                    "event": "pause",
                    "executionId": execution_id,
                    "nodeId": event.node_id,
                    "question": event.payload.get("question", ""),
                    "traceItems": state.trace_items,
                })
            elif event.type == EventType.WF_DONE:
                # handled after loop with full trace items
                pass

        # HITL pause: traversal stopped awaiting a human answer. The ``pause``
        # frame was already emitted; do NOT send wf_done.
        if state.status == "paused":
            return

        # A node failed under onError=abort, or the run was cancelled: report the
        # stop, never a "completed" outcome built from missing upstream output.
        if state.status in ("failed", "cancelled"):
            yield _sse({
                "event": "wf_error",
                "executionId": execution_id,
                "detail": state.error,
                "cancelled": state.status == "cancelled",
                "traceItems": state.trace_items,
            })
            return

        if not state.reached_end:
            state.result = assemble_final_result(state.node_outputs, runner.node_map)

        yield _sse({
            "event": "wf_done",
            "executionId": execution_id,
            "result": state.result.strip(),
            "traceItems": state.trace_items,
        })
    except Exception as exc:  # noqa: BLE001  (mirror run_sync catch-all)
        yield _sse({
            "event": "wf_error",
            "executionId": execution_id,
            "detail": f"执行工作流时发生错误: {str(exc)}",
            "traceItems": state.trace_items,
        })


async def _stream_workflow(
    workflow_id: str,
    workflow: dict,
    context: dict,
    user_id: str = "",
    services: Optional[dict] = None,
    *,
    trigger_kind: str = "designer",
):
    """Yield SSE frames describing a fresh graph execution as it happens."""
    execution_id = str(uuid.uuid4())
    state = ExecutionState(
        execution_id=execution_id,
        workflow_id=workflow_id,
        context=dict(context),
    )
    stop = _begin_run(execution_id, user_id, workflow_id)
    runner = WorkflowRunner(
        workflow,
        state,
        cancel_check=stop.is_set,
        services=services or {},
        recorder=RunRecorder(
            state, workflow_id, _run_meta(workflow, context, user_id, trigger_kind)
        ),
    )
    try:
        async for frame in _stream_events(execution_id, workflow_id, state, runner):
            yield frame
    finally:
        # Reaching this while the traversal is unfinished means the client went
        # away; stop the run instead of leaving it burning tokens unobserved.
        stop.set()
        _end_run(execution_id)


async def _stream_resume_workflow(
    execution_id: str,
    answer: str,
    user_id: str = "",
    services: Optional[dict] = None,
):
    """Continue a HITL-paused execution, streaming the remaining frames.

    Consumes the persisted pause position via :func:`prepare_resume` (which
    removes it from the registry) and drives the traversal from there. If the
    run pauses again on another ask node, a further ``pause`` frame is emitted.
    ``services`` must be re-resolved by the caller: the snapshot on disk holds
    no live handles, the resuming process supplies them.
    """
    prepared = prepare_resume(
        execution_id,
        answer,
        services,
        meta=RunMeta(owner_user_id=user_id or "default", trigger_kind="resume"),
    )
    if prepared is None:
        yield _sse({
            "event": "wf_error",
            "executionId": execution_id,
            "detail": f"暂停中的执行不存在或已过期: {execution_id}",
            "traceItems": [],
        })
        return
    state, runner = prepared
    stop = _begin_run(execution_id, user_id, state.workflow_id)
    runner.cancel_check = stop.is_set
    try:
        async for frame in _stream_events(
            state.execution_id, state.workflow_id, state, runner
        ):
            yield frame
    finally:
        stop.set()
        _end_run(execution_id)



async def execute_workflow_stream(
    workflow_id: str,
    req: ExecuteRequest,
    preview: bool = False,
    ctx: PawAppContext = Depends(get_scoped_ctx),
):
    """Stream workflow execution progress as Server-Sent Events.

    Uses the same graph engine and deployed-version isolation as ``/execute``,
    but surfaces each node transition live so the canvas can highlight the
    currently executing node. Kept as a separate endpoint (rather than a
    ``req.stream`` flag on ``/execute``) so existing synchronous callers are
    completely unaffected.
    """
    workflow = await _resolve_execution_workflow(workflow_id, preview, ctx.user_id)
    context = _build_execution_context(req, ctx)
    services = await _build_tool_services(ctx)
    return StreamingResponse(
        _stream_workflow(
            workflow_id,
            workflow,
            context,
            ctx.user_id,
            services=services,
            trigger_kind="designer" if preview else "deployed_api",
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )



async def resume_workflow(
    workflow_id: str,
    req: ResumeRequest,
    ctx: PawAppContext = Depends(get_scoped_ctx),
) -> dict:
    """Continue a HITL-paused execution with the human answer (JSON contract).

    Mirrors ``/execute``: returns the legacy response shape, either the final
    ``completed`` result or a further ``paused`` outcome when the continuation
    reaches another ask node. Returns 404 when the paused execution is unknown
    or has expired.
    """
    _require_paused_owner(req.execution_id, ctx.user_id)
    services = await _build_tool_services(ctx)
    result = await resume_workflow_sync(
        req.execution_id,
        req.answer,
        services=services,
        meta=RunMeta(owner_user_id=ctx.user_id or "default", trigger_kind="resume"),
    )
    if not result.get("success") and "不存在或已过期" in str(result.get("detail", "")):
        raise HTTPException(status_code=404, detail=result.get("detail", "Paused execution not found"))
    return result



async def resume_workflow_stream(
    workflow_id: str,
    req: ResumeRequest,
    ctx: PawAppContext = Depends(get_scoped_ctx),
):
    """Continue a HITL-paused execution, streaming the remaining SSE frames.

    Uses the same event contract as ``/execute/stream`` so the canvas keeps the
    live execution running from the paused position.
    """
    _require_paused_owner(req.execution_id, ctx.user_id)
    services = await _build_tool_services(ctx)
    return StreamingResponse(
        _stream_resume_workflow(req.execution_id, req.answer, ctx.user_id, services=services),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )



async def cancel_execution(
    workflow_id: str,
    execution_id: str,
    req: Optional[CancelRequest] = None,
    ctx: PawAppContext = Depends(get_scoped_ctx),
) -> dict:
    """Ask a running execution to stop before its next node.

    The flag is polled between nodes, so the node currently in flight finishes
    first — an LLM call is not cut off mid-request. The run reports
    ``cancelled`` and every node that never started is recorded as ``skipped``.
    """
    entry = _ACTIVE_RUNS.get(execution_id)
    if entry is None or entry.workflow_id != workflow_id:
        raise HTTPException(
            status_code=404,
            detail={
                "error_type": "execution_not_found",
                "message": "该执行记录不存在，或不属于当前工作流",
                "action": "refresh",
            },
        )
    if entry.owner and entry.owner != ctx.user_id:
        raise HTTPException(
            status_code=403,
            detail={
                "error_type": "permission_denied",
                "message": "该执行由其他用户发起，无法代为取消",
                "action": "switch_account",
            },
        )
    entry.stop.set()
    return {
        "success": True,
        "data": {
            "execution_id": execution_id,
            "workflow_id": workflow_id,
            "status": "cancelling",
            "reason": (req.reason if req else "") or "",
        },
    }



# ── Execution history (read-only) ───────────────────────────────────

#: Largest page the history API will serve: a caller must not be able to ask for
#: the whole table in one request.
_EXECUTION_PAGE_MAX = 100


async def list_executions(
    workflow_id: str,
    limit: int = 20,
    offset: int = 0,
    status: Optional[str] = None,
    ctx: PawAppContext = Depends(get_scoped_ctx),
) -> dict:
    """This user's runs of one workflow, newest first.

    ``run_db`` is synchronous sqlite3, so the read runs on a worker thread: the
    same reason the recorder writes there — history must never stall a run.
    """
    if status and status not in _RUN_STATUSES:
        raise HTTPException(
            status_code=422,
            detail={
                "error_type": "invalid_status_filter",
                "message": (
                    f"未知的执行状态「{status}」，"
                    f"可选值：{'、'.join(sorted(_RUN_STATUSES))}"
                ),
                "action": "refresh",
            },
        )
    async with _LOCK(workflow_id):
        wf = _find_workflow(workflow_id)
    if wf is None:
        raise HTTPException(
            status_code=404,
            detail={
                "error_type": "workflow_not_found",
                "message": "工作流不存在",
                "action": "请刷新页面或重新选择工作流",
            },
        )
    _require_owner(wf, ctx.user_id, "查看执行历史")

    rows = await asyncio.to_thread(
        _list_runs,
        workflow_id,
        ctx.user_id or "default",
        limit=min(max(limit, 1), _EXECUTION_PAGE_MAX),
        offset=max(offset, 0),
        status=status,
    )
    return {"success": True, "data": rows}


async def get_execution_detail(
    workflow_id: str,
    execution_id: str,
    ctx: PawAppContext = Depends(get_scoped_ctx),
) -> dict:
    """One run read back whole: the trace plus one row per traversed node.

    A run that is not yours and a run that never happened get the same answer,
    because ``get_run`` cannot tell them apart — and telling them apart would
    confirm which execution ids exist under other owners.
    """
    async with _LOCK(workflow_id):
        wf = _find_workflow(workflow_id)
    if wf is None:
        raise HTTPException(
            status_code=404,
            detail={
                "error_type": "workflow_not_found",
                "message": "工作流不存在",
                "action": "请刷新页面或重新选择工作流",
            },
        )
    _require_owner(wf, ctx.user_id, "查看执行历史")

    owner = ctx.user_id or "default"
    run = await asyncio.to_thread(_get_run, execution_id, owner)
    if run is None or run.get("workflow_id") != workflow_id:
        raise HTTPException(
            status_code=404,
            detail={
                "error_type": "execution_not_found",
                "message": "该执行记录不存在，或不属于当前工作流",
                "action": "refresh",
            },
        )
    run["nodes"] = await asyncio.to_thread(_list_run_nodes, execution_id, owner)
    return {"success": True, "data": run}



def register_routes(router: APIRouter) -> None:
    """Apply the original route decorators, in BASE main.py order."""
    router.post("/workflows/{workflow_id}/execute")(execute_workflow)
    router.post("/workflows/{workflow_id}/run")(run_workflow)
    router.post("/workflows/{workflow_id}/execute/stream")(execute_workflow_stream)
    router.post("/workflows/{workflow_id}/execute/resume")(resume_workflow)
    router.post("/workflows/{workflow_id}/execute/resume/stream")(resume_workflow_stream)
    router.post("/workflows/{workflow_id}/executions/{execution_id}/cancel")(cancel_execution)
    router.get("/workflows/{workflow_id}/executions")(list_executions)
    router.get("/workflows/{workflow_id}/executions/{execution_id}")(get_execution_detail)
