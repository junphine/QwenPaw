# -*- coding: utf-8 -*-
"""Node-level retry + timeout policy (pure stdlib).

Kept in the engine layer — which deliberately never imports web/platform — so
retry semantics are testable without FastAPI. The runner parses a node's flat
config keys into a frozen ``RetryPolicy`` and drives an attempt loop from it.
"""

from __future__ import annotations

import dataclasses
from typing import Any, Dict, Optional

#: Which node types opt into retry/timeout.
#: start/end/ask stay out: start/end are trivial, ask pauses the run
#: immediately (WF_PAUSE) so the attempt loop never sees a failure.
RETRY_ENABLED_TYPES = frozenset({"agent", "tool", "router"})

_DEFAULT_MAX_RETRIES = 0
_DEFAULT_BASE_DELAY_SEC = 1.0
_DEFAULT_MAX_DELAY_SEC = 30.0
_MAX_RETRIES_CAP = 10
_MAX_TIMEOUT_SEC = 3600.0


@dataclasses.dataclass(frozen=True)
class RetryPolicy:
    max_retries: int = _DEFAULT_MAX_RETRIES
    base_delay_sec: float = _DEFAULT_BASE_DELAY_SEC
    max_delay_sec: float = _DEFAULT_MAX_DELAY_SEC
    node_timeout_sec: Optional[float] = None

    def with_retries_disabled(self) -> "RetryPolicy":
        """Derive a copy that runs once but keeps the timeout (HITL
        suppression).
        """
        return dataclasses.replace(self, max_retries=0)


def _as_float(value: Any, default: float) -> float:
    if isinstance(value, bool):
        return default
    if isinstance(value, (int, float)):
        return float(value)
    return default


def parse_retry_policy(config: Optional[Dict[str, Any]]) -> RetryPolicy:
    """Read flat retry keys, fail-safe to defaults on dirty. Never raises.

    The publish gate is the authoritative validator; this is the runtime
    backstop so a persisted snapshot with junk values still runs
    conservatively.
    """
    cfg = config or {}

    raw_retries = cfg.get("maxRetries", _DEFAULT_MAX_RETRIES)
    if isinstance(raw_retries, bool) or not isinstance(raw_retries, int):
        max_retries = _DEFAULT_MAX_RETRIES
    elif raw_retries < 0 or raw_retries > _MAX_RETRIES_CAP:
        max_retries = _DEFAULT_MAX_RETRIES
    else:
        max_retries = raw_retries

    base = _as_float(
        cfg.get("retryBaseDelaySec", _DEFAULT_BASE_DELAY_SEC),
        _DEFAULT_BASE_DELAY_SEC,
    )
    if base <= 0:
        base = _DEFAULT_BASE_DELAY_SEC

    maximum = _as_float(
        cfg.get("retryMaxDelaySec", _DEFAULT_MAX_DELAY_SEC),
        _DEFAULT_MAX_DELAY_SEC,
    )
    if maximum <= 0:
        maximum = _DEFAULT_MAX_DELAY_SEC
    if maximum < base:
        maximum = base

    raw_timeout = cfg.get("nodeTimeoutSec")
    timeout: Optional[float] = None
    if raw_timeout is not None:
        t = _as_float(raw_timeout, -1.0)
        if 0 < t <= _MAX_TIMEOUT_SEC:
            timeout = t

    return RetryPolicy(max_retries, base, maximum, timeout)


def backoff_delay(policy: RetryPolicy, retry_index: int) -> float:
    """Exponential backoff capped at max_delay_sec. retry_index is 1-based."""
    if retry_index < 1:
        retry_index = 1
    delay = policy.base_delay_sec * (2 ** (retry_index - 1))
    return min(delay, policy.max_delay_sec)
