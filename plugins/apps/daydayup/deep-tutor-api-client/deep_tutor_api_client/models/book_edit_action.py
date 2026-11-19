from typing import Literal

BookEditAction = Literal[
    "add_chapter",
    "add_page",
    "delete_chapter",
    "delete_page",
    "extend_page",
    "insert_block",
    "move_chapter",
    "move_page",
    "rename_chapter",
    "rename_page",
]

BOOK_EDIT_ACTION_VALUES: set[BookEditAction] = {
    "add_chapter",
    "add_page",
    "delete_chapter",
    "delete_page",
    "extend_page",
    "insert_block",
    "move_chapter",
    "move_page",
    "rename_chapter",
    "rename_page",
}


def check_book_edit_action(value: str) -> BookEditAction:
    if value in BOOK_EDIT_ACTION_VALUES:
        return value
    raise TypeError(f"Unexpected value {value!r}. Expected one of {BOOK_EDIT_ACTION_VALUES!r}")
