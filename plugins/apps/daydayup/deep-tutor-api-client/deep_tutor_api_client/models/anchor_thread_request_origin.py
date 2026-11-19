from typing import Literal

AnchorThreadRequestOrigin = Literal["ask", "generate"]

ANCHOR_THREAD_REQUEST_ORIGIN_VALUES: set[AnchorThreadRequestOrigin] = {
    "ask",
    "generate",
}


def check_anchor_thread_request_origin(value: str) -> AnchorThreadRequestOrigin:
    if value in ANCHOR_THREAD_REQUEST_ORIGIN_VALUES:
        return value
    raise TypeError(f"Unexpected value {value!r}. Expected one of {ANCHOR_THREAD_REQUEST_ORIGIN_VALUES!r}")
