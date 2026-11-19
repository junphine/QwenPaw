from typing import Literal

RuntimeStatusRedisStatus = Literal["not_configured", "ok", "unavailable"]

RUNTIME_STATUS_REDIS_STATUS_VALUES: set[RuntimeStatusRedisStatus] = {
    "not_configured",
    "ok",
    "unavailable",
}


def check_runtime_status_redis_status(value: str) -> RuntimeStatusRedisStatus:
    if value in RUNTIME_STATUS_REDIS_STATUS_VALUES:
        return value
    raise TypeError(f"Unexpected value {value!r}. Expected one of {RUNTIME_STATUS_REDIS_STATUS_VALUES!r}")
