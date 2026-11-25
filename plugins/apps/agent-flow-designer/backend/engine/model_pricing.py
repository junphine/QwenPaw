# -*- coding: utf-8 -*-
"""Model pricing table for token cost calculation.

A simple in-memory price table keyed by model identifier.
Prices are in CNY per 1 000 tokens (both prompt and completion).

The table can be extended via :func:`register_price` at runtime or loaded from
an external config file in the future.  Unknown models fall back to a
generic default so that cost estimation never blocks on a missing entry.
"""

from typing import Dict, Optional

#: Default price for unknown models (CNY per 1 000 tokens).
DEFAULT_PRICE_PER_K = 0.02

#: Price table: model_id -> {"prompt": float, "completion": float}
# All prices in CNY per 1 000 tokens.
# "*" is a wildcard prefix; the longest matching prefix wins.
_PRICES: Dict[str, Dict[str, float]] = {
    # Alibaba DashScope
    "qwen-turbo": {"prompt": 0.02, "completion": 0.02},
    "qwen-plus": {"prompt": 0.04, "completion": 0.04},
    "qwen-max": {"prompt": 0.12, "completion": 0.12},
    "qwen-max-longcontext": {"prompt": 0.12, "completion": 0.12},
    "qwen-coder-plus": {"prompt": 0.04, "completion": 0.04},
    "qwen-coder-turbo": {"prompt": 0.02, "completion": 0.02},
    # OpenAI compatible
    "gpt-3.5-turbo": {"prompt": 0.015, "completion": 0.02},
    "gpt-4": {"prompt": 0.21, "completion": 0.42},
    "gpt-4-turbo": {"prompt": 0.10, "completion": 0.30},
    "gpt-4o": {"prompt": 0.05, "completion": 0.015},
    "gpt-4o-mini": {"prompt": 0.0015, "completion": 0.006},
    # Anthropic
    "claude-3-opus": {"prompt": 0.42, "completion": 2.10},
    "claude-3-sonnet": {"prompt": 0.09, "completion": 0.45},
    "claude-3-haiku": {"prompt": 0.003, "completion": 0.015},
    # Default fallback
    "default": {"prompt": DEFAULT_PRICE_PER_K, "completion": DEFAULT_PRICE_PER_K},
}


def register_price(model_id: str, prompt_price: float, completion_price: Optional[float] = None) -> None:
    """Register or override a model's price at runtime.

    Args:
        model_id: Model identifier (e.g. ``"qwen-plus"``).
        prompt_price: Price in CNY per 1 000 prompt tokens.
        completion_price: Price in CNY per 1 000 completion tokens.
            If omitted, defaults to ``prompt_price``.
    """
    _PRICES[model_id] = {
        "prompt": prompt_price,
        "completion": completion_price if completion_price is not None else prompt_price,
    }


def get_price(model_id: str) -> Dict[str, float]:
    """Return the price dict for *model_id*, falling back to the longest
    prefix match and finally ``"default"``.
    """
    if model_id in _PRICES:
        return _PRICES[model_id]

    # Prefix match: find the longest registered prefix
    best_prefix = ""
    best_price = _PRICES.get("default", {"prompt": DEFAULT_PRICE_PER_K, "completion": DEFAULT_PRICE_PER_K})
    for prefix, price in _PRICES.items():
        if prefix == "default":
            continue
        if model_id.startswith(prefix) and len(prefix) > len(best_prefix):
            best_prefix = prefix
            best_price = price
    return best_price


def calculate_cost(model_id: str, prompt_tokens: int, completion_tokens: int) -> Dict[str, float]:
    """Calculate the cost for a given model and token usage.

    Returns a dict with:
        - prompt_cost: CNY
        - completion_cost: CNY
        - total_cost: CNY
        - model_id: the model identifier used
        - price_per_k_prompt: CNY / 1k tokens
        - price_per_k_completion: CNY / 1k tokens
    """
    price = get_price(model_id)
    prompt_cost = (prompt_tokens / 1000) * price["prompt"]
    completion_cost = (completion_tokens / 1000) * price["completion"]
    return {
        "prompt_cost": round(prompt_cost, 6),
        "completion_cost": round(completion_cost, 6),
        "total_cost": round(prompt_cost + completion_cost, 6),
        "model_id": model_id,
        "price_per_k_prompt": price["prompt"],
        "price_per_k_completion": price["completion"],
    }


def list_known_models() -> Dict[str, Dict[str, float]]:
    """Return a copy of the current price table (excluding the default entry)."""
    return {k: v.copy() for k, v in _PRICES.items() if k != "default"}
