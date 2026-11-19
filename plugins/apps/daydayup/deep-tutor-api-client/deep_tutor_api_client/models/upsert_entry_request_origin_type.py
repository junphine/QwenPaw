from typing import Literal

UpsertEntryRequestOriginType = Literal["conversation", "document_analysis", "external_import"]

UPSERT_ENTRY_REQUEST_ORIGIN_TYPE_VALUES: set[UpsertEntryRequestOriginType] = {
    "conversation",
    "document_analysis",
    "external_import",
}


def check_upsert_entry_request_origin_type(value: str) -> UpsertEntryRequestOriginType:
    if value in UPSERT_ENTRY_REQUEST_ORIGIN_TYPE_VALUES:
        return value
    raise TypeError(f"Unexpected value {value!r}. Expected one of {UPSERT_ENTRY_REQUEST_ORIGIN_TYPE_VALUES!r}")
