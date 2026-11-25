# -*- coding: utf-8 -*-
"""Execution replay: replay a past run from its stored trace without calling
any external service.

Replay reads ``execution_runs.trace_json`` and ``execution_nodes`` rows and
turns them back into a stream of :class:`RunEvent` objects so that the same
consumer (SSE, polling, etc.) can display them without knowing whether the run
is live or historical.
"""

import asyncio
import json
from typing import Any, AsyncIterator, Dict, List, Optional

from .log_context import get_logger

logger = get_logger(__name__)


async def replay_execution(
    run_record: Dict[str, Any],
    nodes: List[Dict[str, Any]],
    *,
    delay_ms: float = 0.0,
) -> AsyncIterator[Dict[str, Any]]:
    """Yield replay events for a stored execution.

    Args:
        run_record: A row from ``run_db.get_run`` (must include ``trace_items``).
        nodes: Node rows from ``run_db.list_nodes`` (ordered by ``seq``).
        delay_ms: Artificial delay between events (ms). 0 means instant replay.

    Yields dicts with keys:
        - type: "node_start" | "node_done" | "node_error" | "route" | "wf_start" | "wf_done"
        - node_id: str (optional)
        - trace: dict (optional)
        - payload: dict (optional)
        - replay: True (always set so the consumer can tell)
    """
    execution_id = run_record.get("execution_id", "unknown")
    logger.info("[Replay] Starting replay for execution_id=%s nodes=%d", execution_id, len(nodes))

    # Yield workflow start
    yield {
        "type": "wf_start",
        "payload": {"workflowId": run_record.get("workflow_id"), "resumed": False, "replay": True},
        "replay": True,
    }

    if delay_ms > 0:
        await asyncio.sleep(delay_ms / 1000)

    # Replay each node
    for node in nodes:
        node_id = node.get("node_id", "unknown")
        status = node.get("status", "completed")
        trace = _build_node_trace(node)

        # Yield node_start
        yield {
            "type": "node_start",
            "node_id": node_id,
            "payload": {"nodeLabel": node.get("node_label", node_id), "type": node.get("node_type", "")},
            "replay": True,
        }

        if delay_ms > 0:
            await asyncio.sleep(delay_ms / 1000)

        # Yield node_done / node_error / route
        if status == "failed":
            yield {
                "type": "node_error",
                "node_id": node_id,
                "trace": trace,
                "replay": True,
            }
        else:
            yield {
                "type": "node_done",
                "node_id": node_id,
                "trace": trace,
                "replay": True,
            }

        if delay_ms > 0:
            await asyncio.sleep(delay_ms / 1000)

    # Yield workflow done
    yield {
        "type": "wf_done",
        "payload": {
            "result": run_record.get("result_text", ""),
            "status": run_record.get("status", "completed"),
        },
        "replay": True,
    }

    logger.info("[Replay] Finished replay for execution_id=%s", execution_id)


def _build_node_trace(node: Dict[str, Any]) -> Dict[str, Any]:
    """Build a trace dict from a stored node row."""
    return {
        "nodeId": node.get("node_id", ""),
        "nodeLabel": node.get("node_label", ""),
        "type": node.get("node_type", ""),
        "status": node.get("status", "completed"),
        "durationMs": node.get("duration_ms", 0),
        "promptTokens": node.get("prompt_tokens", 0),
        "completionTokens": node.get("completion_tokens", 0),
        "totalTokens": node.get("total_tokens", 0),
        "inputs": node.get("inputs"),
        "output": node.get("output"),
        "message": node.get("message", ""),
        "error": node.get("error", ""),
        "replay": True,
    }


async def replay_execution_sync(
    run_record: Dict[str, Any],
    nodes: List[Dict[str, Any]],
    *,
    delay_ms: float = 0.0,
) -> Dict[str, Any]:
    """Synchronous-style replay: collect all events into a single response dict.

    Returns a dict compatible with the ``/execute`` response format.
    """
    events = []
    async for event in replay_execution(run_record, nodes, delay_ms=delay_ms):
        events.append(event)

    return {
        "success": True,
        "data": {
            "execution_id": run_record.get("execution_id", ""),
            "status": "completed",
            "result": "[重放模式] 本次执行仅为历史记录回放，未调用任何外部服务。",
            "trace": {
                "workflowId": run_record.get("workflow_id", ""),
                "status": "completed",
                "items": events,
            },
            "replay": True,
        },
    }
