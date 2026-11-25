"""Tests for synchronous execution cancellation (Scheme C).

Verifies that /execute and /run endpoints can be cancelled via /cancel,
matching the streaming path's behaviour.
"""

import asyncio
import uuid
import pytest
from typing import Dict, Any

from engine.state import ExecutionState
from engine.runner import WorkflowRunner, run_workflow_sync
from engine.registry import register_node, _REGISTRY
from engine.events import RunEvent, EventType


# ── Mock handlers for testing ───────────────────────────────────────

async def _mock_start_handler(ctx):
    """Start node that yields immediately."""
    from engine.events import RunEvent, EventType
    yield RunEvent(EventType.NODE_DONE, ctx.node_id, {"trace": {"status": "completed"}})


async def _mock_slow_handler(ctx):
    """Node that sleeps for a configurable duration."""
    from engine.events import RunEvent, EventType
    delay = ctx.config.get("delay", 1.0)
    await asyncio.sleep(delay)
    yield RunEvent(EventType.NODE_DONE, ctx.node_id, {"trace": {"status": "completed"}})


async def _mock_end_handler(ctx):
    """End node that signals completion."""
    from engine.events import RunEvent, EventType
    yield RunEvent(EventType.NODE_DONE, ctx.node_id, {"trace": {"status": "completed"}})
    yield RunEvent(EventType.WF_DONE, ctx.node_id, {"result": "done"})


def _register_test_handlers():
    """Register mock handlers for test nodes."""
    from engine import registry as reg
    reg._REGISTRY["start"] = (_mock_start_handler, None)
    reg._REGISTRY["mock_slow"] = (_mock_slow_handler, None)
    reg._REGISTRY["end"] = (_mock_end_handler, None)


def _make_node(node_id: str, node_type: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
    """Create a minimal node definition."""
    return {
        "id": node_id,
        "type": node_type,
        "label": node_id,
        "config": config or {},
    }


def _make_edge(source: str, target: str) -> Dict[str, Any]:
    """Create a minimal edge definition."""
    return {
        "source": source,
        "target": target,
    }


def _build_workflow(nodes, edges):
    """Build a minimal workflow definition."""
    return {
        "nodes": nodes,
        "edges": edges,
    }


# ── Tests ───────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def setup_handlers():
    """Ensure mock handlers are registered before each test."""
    _register_test_handlers()
    yield
    # Cleanup is not needed as tests use isolated registries


class TestSyncCancellation:
    """Test synchronous execution cancellation."""

    @pytest.mark.asyncio
    async def test_sync_execute_can_be_cancelled(self):
        """Verify that a sync /execute run can be cancelled mid-flight."""
        # Build a workflow with multiple slow nodes
        wf = _build_workflow(
            nodes=[
                _make_node("start", "start"),
                _make_node("slow1", "mock_slow", {"delay": 0.3}),
                _make_node("slow2", "mock_slow", {"delay": 2.0}),
                _make_node("end", "end"),
            ],
            edges=[
                _make_edge("start", "slow1"),
                _make_edge("slow1", "slow2"),
                _make_edge("slow2", "end"),
            ],
        )

        context = {"user_input": "test"}
        
        # Create a cancel flag
        cancel_flag = asyncio.Event()
        
        # Pre-create execution_id for cancellation
        execution_id = str(uuid.uuid4())
        
        # Start the sync execution in background
        async def run_with_cancel():
            result = await run_workflow_sync(
                workflow_id="wf-test",
                workflow=wf,
                context=context,
                execution_id=execution_id,
                cancel_check=cancel_flag.is_set,
            )
            return result
        
        task = asyncio.create_task(run_with_cancel())
        
        # Wait for first slow node to complete
        await asyncio.sleep(0.5)
        
        # Cancel before second slow node starts
        cancel_flag.set()
        
        # Wait for the task to complete
        result = await asyncio.wait_for(task, timeout=5.0)
        
        # Verify the run was cancelled
        assert result["success"] is False
        assert result["data"]["status"] == "cancelled"
        assert "取消" in result["data"]["result"]

    @pytest.mark.asyncio
    async def test_sync_run_endpoint_can_be_cancelled(self):
        """Verify that /run endpoint (deployed workflows) supports cancellation."""
        # Same test structure but simulating deployed workflow execution
        wf = _build_workflow(
            nodes=[
                _make_node("start", "start"),
                _make_node("slow", "mock_slow", {"delay": 3.0}),
                _make_node("end", "end"),
            ],
            edges=[
                _make_edge("start", "slow"),
                _make_edge("slow", "end"),
            ],
        )

        context = {"user_input": "test"}
        cancel_flag = asyncio.Event()
        execution_id = str(uuid.uuid4())
        
        async def run_with_cancel():
            result = await run_workflow_sync(
                workflow_id="wf-deployed",
                workflow=wf,
                context=context,
                execution_id=execution_id,
                cancel_check=cancel_flag.is_set,
            )
            return result
        
        task = asyncio.create_task(run_with_cancel())
        await asyncio.sleep(0.3)
        cancel_flag.set()
        
        result = await asyncio.wait_for(task, timeout=5.0)
        
        assert result["success"] is False
        assert result["data"]["status"] == "cancelled"

    @pytest.mark.asyncio
    async def test_cancel_before_start_aborts_immediately(self):
        """Verify that cancelling before execution aborts at first check point."""
        wf = _build_workflow(
            nodes=[
                _make_node("start", "start"),
                _make_node("end", "end"),
            ],
            edges=[
                _make_edge("start", "end"),
            ],
        )

        context = {"user_input": "test"}
        cancel_flag = asyncio.Event()
        cancel_flag.set()  # Set before starting
        
        result = await run_workflow_sync(
            workflow_id="wf-test",
            workflow=wf,
            context=context,
            cancel_check=cancel_flag.is_set,
        )
        
        # Cancel is checked at the start of the while loop, so it aborts immediately
        assert result["success"] is False
        assert result["data"]["status"] == "cancelled"

    @pytest.mark.asyncio
    async def test_cancel_between_nodes_records_cancelled(self):
        """Verify cancellation is recorded when set between nodes."""
        wf = _build_workflow(
            nodes=[
                _make_node("start", "start"),
                _make_node("fast", "mock_slow", {"delay": 0.1}),
                _make_node("medium", "mock_slow", {"delay": 2.0}),
            ],
            edges=[
                _make_edge("start", "fast"),
                _make_edge("fast", "medium"),
            ],
        )

        context = {"user_input": "test"}
        cancel_flag = asyncio.Event()
        execution_id = str(uuid.uuid4())
        
        async def run_with_cancel():
            result = await run_workflow_sync(
                workflow_id="wf-test",
                workflow=wf,
                context=context,
                execution_id=execution_id,
                cancel_check=cancel_flag.is_set,
            )
            return result
        
        task = asyncio.create_task(run_with_cancel())
        # Cancel very quickly, after start but before medium node starts
        await asyncio.sleep(0.05)  # fast node takes 0.1s
        cancel_flag.set()
        
        result = await asyncio.wait_for(task, timeout=5.0)
        
        assert result["success"] is False
        assert result["data"]["status"] == "cancelled"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
