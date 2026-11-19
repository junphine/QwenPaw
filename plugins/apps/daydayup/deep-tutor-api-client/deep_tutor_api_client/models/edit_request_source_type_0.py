from typing import Literal

EditRequestSourceType0 = Literal["rag", "web"]

EDIT_REQUEST_SOURCE_TYPE_0_VALUES: set[EditRequestSourceType0] = {
    "rag",
    "web",
}


def check_edit_request_source_type_0(value: str) -> EditRequestSourceType0:
    if value in EDIT_REQUEST_SOURCE_TYPE_0_VALUES:
        return value
    raise TypeError(f"Unexpected value {value!r}. Expected one of {EDIT_REQUEST_SOURCE_TYPE_0_VALUES!r}")
