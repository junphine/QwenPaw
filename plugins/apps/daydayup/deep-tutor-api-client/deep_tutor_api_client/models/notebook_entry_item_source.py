from typing import Literal

NotebookEntryItemSource = Literal[
    "book", "deep_question", "immersive_reading", "import", "mastery_path", "partner_chat"
]

NOTEBOOK_ENTRY_ITEM_SOURCE_VALUES: set[NotebookEntryItemSource] = {
    "book",
    "deep_question",
    "immersive_reading",
    "import",
    "mastery_path",
    "partner_chat",
}


def check_notebook_entry_item_source(value: str) -> NotebookEntryItemSource:
    if value in NOTEBOOK_ENTRY_ITEM_SOURCE_VALUES:
        return value
    raise TypeError(f"Unexpected value {value!r}. Expected one of {NOTEBOOK_ENTRY_ITEM_SOURCE_VALUES!r}")
