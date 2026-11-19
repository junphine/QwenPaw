from typing import Literal

RuntimeStatusCoordinationMode = Literal["memory", "redis"]

RUNTIME_STATUS_COORDINATION_MODE_VALUES: set[RuntimeStatusCoordinationMode] = {
    "memory",
    "redis",
}


def check_runtime_status_coordination_mode(value: str) -> RuntimeStatusCoordinationMode:
    if value in RUNTIME_STATUS_COORDINATION_MODE_VALUES:
        return value
    raise TypeError(f"Unexpected value {value!r}. Expected one of {RUNTIME_STATUS_COORDINATION_MODE_VALUES!r}")
