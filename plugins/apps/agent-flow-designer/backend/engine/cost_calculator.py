# -*- coding: utf-8 -*-
"""Cost calculation for workflow executions.

Aggregates token usage from ``execution_nodes`` and turns it into a human-readable
cost summary using :mod:`engine.model_pricing`.
"""

from typing import Any, Dict, List, Optional

from . import model_pricing


def calculate_run_cost(nodes: List[Dict[str, Any]], *, model_id: str = "default") -> Dict[str, Any]:
    """Calculate the total cost for a run from its node rows.

    Args:
        nodes: List of node dicts (from ``run_db.list_nodes``).
        model_id: The model identifier used for cost calculation.
            Defaults to ``"default"`` if not known.

    Returns a dict with:
        - prompt_tokens: int
        - completion_tokens: int
        - total_tokens: int
        - prompt_cost: float (CNY)
        - completion_cost: float (CNY)
        - total_cost: float (CNY)
        - model_id: str
        - node_breakdown: List[dict] (per-node cost)
    """
    prompt_tokens = 0
    completion_tokens = 0
    total_tokens = 0
    node_breakdown: List[Dict[str, Any]] = []

    for node in nodes:
        pt = node.get("prompt_tokens") or 0
        ct = node.get("completion_tokens") or 0
        tt = node.get("total_tokens") or 0
        prompt_tokens += pt
        completion_tokens += ct
        total_tokens += tt

        if pt or ct:
            cost = model_pricing.calculate_cost(model_id, pt, ct)
            node_breakdown.append({
                "node_id": node.get("node_id", "unknown"),
                "node_label": node.get("node_label", ""),
                "node_type": node.get("node_type", ""),
                "prompt_tokens": pt,
                "completion_tokens": ct,
                "total_tokens": tt,
                "cost": cost["total_cost"],
            })

    # Use the run-level total_tokens for the overall cost calculation
    # (avoids double-counting if individual nodes already sum to total)
    cost = model_pricing.calculate_cost(model_id, prompt_tokens, completion_tokens)

    return {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "prompt_cost": cost["prompt_cost"],
        "completion_cost": cost["completion_cost"],
        "total_cost": cost["total_cost"],
        "model_id": model_id,
        "node_breakdown": node_breakdown,
    }


def enrich_run_with_cost(run: Dict[str, Any], nodes: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Add cost information to an existing run dict.

    The original ``run`` dict is *not* mutated; a new dict is returned.
    """
    # Try to infer model from trace items
    model_id = _infer_model_from_trace(run.get("trace_items", []))
    cost = calculate_run_cost(nodes, model_id=model_id)
    return {**run, "cost": cost}


def _infer_model_from_trace(trace_items: List[Dict[str, Any]]) -> str:
    """Infer the model ID from trace items (agent node outputs)."""
    for item in trace_items:
        if not isinstance(item, dict):
            continue
        # Check for model in agent node output
        output = item.get("output", {})
        if isinstance(output, dict):
            model = output.get("model") or output.get("model_id")
            if model:
                return str(model)
        # Check rawOutput for model hints
        raw = item.get("rawOutput", "")
        if isinstance(raw, str):
            if "gpt-4o" in raw:
                return "gpt-4o"
            if "gpt-4" in raw:
                return "gpt-4"
            if "claude" in raw.lower():
                return "claude-3-sonnet"
            if "qwen" in raw.lower():
                return "qwen-plus"
    return "default"
