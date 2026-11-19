from typing import Literal

UpsertEntryRequestSource = Literal[
    "book", "deep_question", "immersive_reading", "import", "mastery_path", "partner_chat"
]

UPSERT_ENTRY_REQUEST_SOURCE_VALUES: set[UpsertEntryRequestSource] = {
    "book",
    "deep_question",
    "immersive_reading",
    "import",
    "mastery_path",
    "partner_chat",
}


def check_upsert_entry_request_source(value: str) -> UpsertEntryRequestSource:
    if value in UPSERT_ENTRY_REQUEST_SOURCE_VALUES:
        return value
    raise TypeError(f"Unexpected value {value!r}. Expected one of {UPSERT_ENTRY_REQUEST_SOURCE_VALUES!r}")
