# -*- coding: utf-8 -*-
"""RED tests for parallel fan-out and concurrency limit (#1).

Covers:
- Serial execution when concurrency_limit=1 (default).
- Parallel fan-out when concurrency_limit>1 (asyncio.gather).
- Concurrency throttling via asyncio.Semaphore.
- Scope isolation and merging of node_outputs across parallel branches.
- Error handling (onError policies) in parallel branches.
- Cycle detection (back-edges) does not break parallel scheduling.
"""

from __future__ import annotations

import asyncio
import time
from typing import Any, Dict, List

import pytest

from engine.events import EventType, RunEvent
from engine.registry import NodeRunContext, register_node
from engine.runner import WorkflowRunner
from engine.state import ExecutionState

# ── Helpers ─────────────────────────────────────────────────────────────────


def _build_workflow(nodes: List[dict], edges: List[dict]) -> Dict[str, Any]:
    return {"nodes": nodes, "edges": edges}


def _make_node(node_id: str, node_type: str, config: Dict[str, Any] | None = None) -> dict:
    return {"id": node_id, "type": node_type, "label": node_id, "config": config or {}}


def _make_edge(source: str, target: str, source_handle: str = "") -> dict:
    edge: Dict[str, Any] = {"source": source, "target": target}
    if source_handle:
        edge["sourceHandle"] = source_handle
    return edge


# ── Mock handlers (NOT registered at import time) ─────────────────────

# Track execution timing for concurrency assertions
_execution_log: List[Dict[str, Any]] = []


def _clear_log() -> None:
    _execution_log.clear()


def _register_mock_handlers():
    """Register all mock handlers for this test module."""
    from engine import registry as reg
    
    # Register mock handlers (will override any existing ones)
    reg._REGISTRY["start"] = (_mock_start_handler, None)
    reg._REGISTRY["end"] = (_mock_end_handler, None)
    reg._REGISTRY["mock_slow"] = (_mock_slow_handler, None)
    reg._REGISTRY["mock_instant"] = (_mock_instant_handler, None)
    reg._REGISTRY["mock_error"] = (_mock_error_handler, None)


async def _mock_start_handler(ctx: NodeRunContext):
    """Simple start handler."""
    node_id = ctx.node_id
    ctx.state.node_outputs[node_id] = "started"
    yield RunEvent(EventType.NODE_DONE, node_id, {"trace": {"status": "completed"}})


async def _mock_end_handler(ctx: NodeRunContext):
    """Simple end handler that emits WF_DONE."""
    node_id = ctx.node_id
    ctx.state.node_outputs[node_id] = "ended"
    yield RunEvent(EventType.NODE_DONE, node_id, {"trace": {"status": "completed"}})
    yield RunEvent(EventType.WF_DONE, node_id, {"result": "done"})


async def _mock_slow_handler(ctx: NodeRunContext):
    """A slow handler that records start/end times."""
    node_id = ctx.node_id
    config = ctx.config
    delay = config.get("delay", 0.1)
    output = config.get("output", f"output_of_{node_id}")
    _execution_log.append({"event": "start", "node_id": node_id, "ts": time.monotonic()})
    await asyncio.sleep(delay)
    _execution_log.append({"event": "end", "node_id": node_id, "ts": time.monotonic()})
    ctx.state.node_outputs[node_id] = output
    yield RunEvent(EventType.NODE_DONE, node_id, {"trace": {"status": "completed"}})


async def _mock_instant_handler(ctx: NodeRunContext):
    """An instant handler that records execution."""
    node_id = ctx.node_id
    config = ctx.config
    output = config.get("output", f"output_of_{node_id}")
    _execution_log.append({"event": "start", "node_id": node_id, "ts": time.monotonic()})
    _execution_log.append({"event": "end", "node_id": node_id, "ts": time.monotonic()})
    ctx.state.node_outputs[node_id] = output
    yield RunEvent(EventType.NODE_DONE, node_id, {"trace": {"status": "completed"}})


async def _mock_error_handler(ctx: NodeRunContext):
    """A handler that always fails."""
    node_id = ctx.node_id
    _execution_log.append({"event": "error", "node_id": node_id, "ts": time.monotonic()})
    yield RunEvent(
        EventType.NODE_ERROR,
        node_id,
        {"trace": {"status": "failed", "error": "mock error", "message": "intentional failure"}},
    )


# ── Tests ───────────────────────────────────────────────────────────────────


class TestSerialExecution:
    """When concurrency_limit=1 (default), nodes execute one after another."""

    @pytest.mark.asyncio
    async def test_default_concurrency_limit_is_serial(self):
        """Default concurrency_limit=1 runs nodes sequentially."""
        _register_mock_handlers()
        _clear_log()
        wf = _build_workflow(
            nodes=[
                _make_node("start", "start"),
                _make_node("a", "mock_slow"),
                _make_node("b", "mock_slow"),
                _make_node("end", "end"),
            ],
            edges=[
                _make_edge("start", "a"),
                _make_edge("a", "b"),
                _make_edge("b", "end"),
            ],
        )
        state = ExecutionState(execution_id="test-1", workflow_id="wf-1")
        runner = WorkflowRunner(wf, state)

        async for _ in runner.run():
            pass

        # Nodes should complete in order
        assert state.status == "completed"
        assert state.node_outputs.get("a") is not None
        assert state.node_outputs.get("b") is not None


class TestParallelFanOut:
    """When concurrency_limit>1, ready nodes execute concurrently."""

    @pytest.mark.asyncio
    async def test_parallel_fan_out_executes_concurrently(self):
        """A node with two successors runs them in parallel when limit>1."""
        _register_mock_handlers()
        _clear_log()
        wf = _build_workflow(
            nodes=[
                _make_node("start", "start"),
                _make_node("a", "mock_slow", {"delay": 0.2}),
                _make_node("b", "mock_slow", {"delay": 0.2}),
                _make_node("end", "end"),
            ],
            edges=[
                _make_edge("start", "a"),
                _make_edge("start", "b"),
                _make_edge("a", "end"),
                _make_edge("b", "end"),
            ],
        )
        state = ExecutionState(execution_id="test-2", workflow_id="wf-1")
        runner = WorkflowRunner(wf, state, concurrency_limit=2)

        start_ts = time.monotonic()
        async for _ in runner.run():
            pass
        total_time = time.monotonic() - start_ts

        # Parallel execution should take ~0.2s, serial would take ~0.4s
        assert total_time < 0.35, f"Expected parallel execution < 0.35s, took {total_time:.3f}s"

        # Both nodes should have completed
        assert state.node_outputs.get("a") is not None
        assert state.node_outputs.get("b") is not None

        # Verify overlap: one node started before the other finished
        starts = [e for e in _execution_log if e["event"] == "start"]
        ends = [e for e in _execution_log if e["event"] == "end"]
        assert len(starts) == 2
        assert len(ends) == 2
        # At least one start happened before the other end (concurrency evidence)
        earliest_end = min(e["ts"] for e in ends)
        latest_start = max(e["ts"] for e in starts)
        # If truly parallel, starts should be close together and overlap with ends
        assert latest_start < earliest_end + 0.15  # generous tolerance


class TestConcurrencyLimit:
    """asyncio.Semaphore should cap the number of concurrently running nodes."""

    @pytest.mark.asyncio
    async def test_semaphore_limits_concurrent_nodes(self):
        """With limit=2, only 2 of 3 ready nodes run at the same time."""
        _register_mock_handlers()
        _clear_log()
        wf = _build_workflow(
            nodes=[
                _make_node("start", "start"),
                _make_node("a", "mock_slow", {"delay": 0.3}),
                _make_node("b", "mock_slow", {"delay": 0.3}),
                _make_node("c", "mock_slow", {"delay": 0.3}),
                _make_node("end", "end"),
            ],
            edges=[
                _make_edge("start", "a"),
                _make_edge("start", "b"),
                _make_edge("start", "c"),
                _make_edge("a", "end"),
                _make_edge("b", "end"),
                _make_edge("c", "end"),
            ],
        )
        state = ExecutionState(execution_id="test-3", workflow_id="wf-1")
        runner = WorkflowRunner(wf, state, concurrency_limit=2)

        async for _ in runner.run():
            pass

        log = _execution_log
        # Count max overlapping nodes at any point
        max_overlap = 0
        for i, entry in enumerate(log):
            if entry["event"] == "start":
                current = sum(1 for e in log[: i + 1] if e["event"] == "start") - sum(
                    1 for e in log[:i] if e["event"] == "end"
                )
                max_overlap = max(max_overlap, current)

        assert max_overlap <= 2, f"Expected at most 2 concurrent nodes, saw {max_overlap}"


class TestNodeOutputsIsolation:
    """Parallel branches must not corrupt each other's node_outputs."""

    @pytest.mark.asyncio
    async def test_outputs_merged_after_parallel_execution(self):
        """Outputs from parallel branches are all present in state.node_outputs."""
        _register_mock_handlers()
        _clear_log()
        wf = _build_workflow(
            nodes=[
                _make_node("start", "start"),
                _make_node("a", "mock_instant", {"output": "branch_a_result"}),
                _make_node("b", "mock_instant", {"output": "branch_b_result"}),
                _make_node("end", "end"),
            ],
            edges=[
                _make_edge("start", "a"),
                _make_edge("start", "b"),
                _make_edge("a", "end"),
                _make_edge("b", "end"),
            ],
        )
        state = ExecutionState(execution_id="test-4", workflow_id="wf-1")
        runner = WorkflowRunner(wf, state, concurrency_limit=2)

        async for _ in runner.run():
            pass

        assert state.node_outputs.get("a") == "branch_a_result"
        assert state.node_outputs.get("b") == "branch_b_result"
        assert state.node_outputs.get("end") == "ended"


class TestParallelErrorHandling:
    """onError policies must work correctly when nodes run in parallel."""

    @pytest.mark.asyncio
    async def test_on_error_abort_stops_run_in_parallel(self):
        """A failed node with onError=abort stops the entire workflow."""
        _register_mock_handlers()
        wf = _build_workflow(
            nodes=[
                _make_node("start", "start"),
                _make_node("bad", "mock_error", {"onError": "abort"}),
                _make_node("good", "mock_instant"),
                _make_node("end", "end"),
            ],
            edges=[
                _make_edge("start", "bad"),
                _make_edge("start", "good"),
                _make_edge("bad", "end"),
                _make_edge("good", "end"),
            ],
        )
        state = ExecutionState(execution_id="test-5", workflow_id="wf-1")
        runner = WorkflowRunner(wf, state, concurrency_limit=2)

        async for _ in runner.run():
            pass

        assert state.status == "failed"
        # end node should not have run
        assert "end" not in state.node_outputs or state.node_status.get("end") != "completed"

    @pytest.mark.asyncio
    async def test_on_error_continue_allows_run_in_parallel(self):
        """A failed node with onError=continue lets downstream proceed."""
        _register_mock_handlers()
        wf = _build_workflow(
            nodes=[
                _make_node("start", "start"),
                _make_node("bad", "mock_error", {"onError": "continue"}),
                _make_node("good", "mock_instant"),
                _make_node("end", "end"),
            ],
            edges=[
                _make_edge("start", "bad"),
                _make_edge("start", "good"),
                _make_edge("bad", "end"),
                _make_edge("good", "end"),
            ],
        )
        state = ExecutionState(execution_id="test-6", workflow_id="wf-1")
        runner = WorkflowRunner(wf, state, concurrency_limit=2)

        async for _ in runner.run():
            pass

        # With continue, the run may complete or fail depending on barrier logic
        # but end should not be skipped due to the error branch
        assert state.status == "completed"


class TestCycleDetection:
    """Back-edges are detected and ignored by the barrier scheduler."""

    @pytest.mark.asyncio
    async def test_cycle_is_detected_and_handled(self):
        """A cycle in the graph does not hang the runner."""
        _register_mock_handlers()
        wf = _build_workflow(
            nodes=[
                _make_node("start", "start"),
                _make_node("a", "mock_instant"),
                _make_node("b", "mock_instant"),
            ],
            edges=[
                _make_edge("start", "a"),
                _make_edge("a", "b"),
                _make_edge("b", "a"),  # cycle: b -> a
            ],
        )
        state = ExecutionState(execution_id="test-7", workflow_id="wf-1")
        runner = WorkflowRunner(wf, state)

        # Should complete without hanging
        async for _ in runner.run():
            pass

        assert state.status == "completed"
