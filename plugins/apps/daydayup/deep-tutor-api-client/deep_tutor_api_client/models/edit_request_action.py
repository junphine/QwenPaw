from typing import Literal

EditRequestAction = Literal["expand", "rewrite", "shorten"]

EDIT_REQUEST_ACTION_VALUES: set[EditRequestAction] = {
    "expand",
    "rewrite",
    "shorten",
}


def check_edit_request_action(value: str) -> EditRequestAction:
    if value in EDIT_REQUEST_ACTION_VALUES:
        return value
    raise TypeError(f"Unexpected value {value!r}. Expected one of {EDIT_REQUEST_ACTION_VALUES!r}")
