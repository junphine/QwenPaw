from typing import Literal

NotebookEntryItemOriginType = Literal["conversation", "document_analysis", "external_import"]

NOTEBOOK_ENTRY_ITEM_ORIGIN_TYPE_VALUES: set[NotebookEntryItemOriginType] = {
    "conversation",
    "document_analysis",
    "external_import",
}


def check_notebook_entry_item_origin_type(value: str) -> NotebookEntryItemOriginType:
    if value in NOTEBOOK_ENTRY_ITEM_ORIGIN_TYPE_VALUES:
        return value
    raise TypeError(f"Unexpected value {value!r}. Expected one of {NOTEBOOK_ENTRY_ITEM_ORIGIN_TYPE_VALUES!r}")
