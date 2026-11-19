from typing import Literal

DeleteEventsScope = Literal["all", "following", "this"]

DELETE_EVENTS_SCOPE_VALUES: set[DeleteEventsScope] = {
    "all",
    "following",
    "this",
}


def check_delete_events_scope(value: str) -> DeleteEventsScope:
    if value in DELETE_EVENTS_SCOPE_VALUES:
        return value
    raise TypeError(f"Unexpected value {value!r}. Expected one of {DELETE_EVENTS_SCOPE_VALUES!r}")
