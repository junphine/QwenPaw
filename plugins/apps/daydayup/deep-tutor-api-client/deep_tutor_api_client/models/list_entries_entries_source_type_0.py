from typing import Literal

ListEntriesEntriesSourceType0 = Literal[
    "book", "deep_question", "immersive_reading", "import", "mastery_path", "partner_chat"
]

LIST_ENTRIES_ENTRIES_SOURCE_TYPE_0_VALUES: set[ListEntriesEntriesSourceType0] = {
    "book",
    "deep_question",
    "immersive_reading",
    "import",
    "mastery_path",
    "partner_chat",
}


def check_list_entries_entries_source_type_0(value: str) -> ListEntriesEntriesSourceType0:
    if value in LIST_ENTRIES_ENTRIES_SOURCE_TYPE_0_VALUES:
        return value
    raise TypeError(f"Unexpected value {value!r}. Expected one of {LIST_ENTRIES_ENTRIES_SOURCE_TYPE_0_VALUES!r}")
