from typing import Literal

NotebookEntryItemResultType0 = Literal["correct", "incorrect", "partial", "ungraded", "voided"]

NOTEBOOK_ENTRY_ITEM_RESULT_TYPE_0_VALUES: set[NotebookEntryItemResultType0] = {
    "correct",
    "incorrect",
    "partial",
    "ungraded",
    "voided",
}


def check_notebook_entry_item_result_type_0(value: str) -> NotebookEntryItemResultType0:
    if value in NOTEBOOK_ENTRY_ITEM_RESULT_TYPE_0_VALUES:
        return value
    raise TypeError(f"Unexpected value {value!r}. Expected one of {NOTEBOOK_ENTRY_ITEM_RESULT_TYPE_0_VALUES!r}")
