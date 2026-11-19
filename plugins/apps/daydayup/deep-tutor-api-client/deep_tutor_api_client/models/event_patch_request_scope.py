from typing import Literal

EventPatchRequestScope = Literal["all", "following", "this"]

EVENT_PATCH_REQUEST_SCOPE_VALUES: set[EventPatchRequestScope] = {
    "all",
    "following",
    "this",
}


def check_event_patch_request_scope(value: str) -> EventPatchRequestScope:
    if value in EVENT_PATCH_REQUEST_SCOPE_VALUES:
        return value
    raise TypeError(f"Unexpected value {value!r}. Expected one of {EVENT_PATCH_REQUEST_SCOPE_VALUES!r}")
