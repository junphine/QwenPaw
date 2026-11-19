from typing import Literal

ReactEditRequestMode = Literal["expand", "none", "rewrite", "shorten"]

REACT_EDIT_REQUEST_MODE_VALUES: set[ReactEditRequestMode] = {
    "expand",
    "none",
    "rewrite",
    "shorten",
}


def check_react_edit_request_mode(value: str) -> ReactEditRequestMode:
    if value in REACT_EDIT_REQUEST_MODE_VALUES:
        return value
    raise TypeError(f"Unexpected value {value!r}. Expected one of {REACT_EDIT_REQUEST_MODE_VALUES!r}")
