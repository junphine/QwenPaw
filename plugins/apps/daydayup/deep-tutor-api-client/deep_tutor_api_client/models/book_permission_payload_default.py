from typing import Literal

BookPermissionPayloadDefault = Literal["none", "read"]

BOOK_PERMISSION_PAYLOAD_DEFAULT_VALUES: set[BookPermissionPayloadDefault] = {
    "none",
    "read",
}


def check_book_permission_payload_default(value: str) -> BookPermissionPayloadDefault:
    if value in BOOK_PERMISSION_PAYLOAD_DEFAULT_VALUES:
        return value
    raise TypeError(f"Unexpected value {value!r}. Expected one of {BOOK_PERMISSION_PAYLOAD_DEFAULT_VALUES!r}")
