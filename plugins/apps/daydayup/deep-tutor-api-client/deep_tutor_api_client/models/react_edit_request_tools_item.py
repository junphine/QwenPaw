from typing import Literal

ReactEditRequestToolsItem = Literal["rag", "web"]

REACT_EDIT_REQUEST_TOOLS_ITEM_VALUES: set[ReactEditRequestToolsItem] = {
    "rag",
    "web",
}


def check_react_edit_request_tools_item(value: str) -> ReactEditRequestToolsItem:
    if value in REACT_EDIT_REQUEST_TOOLS_ITEM_VALUES:
        return value
    raise TypeError(f"Unexpected value {value!r}. Expected one of {REACT_EDIT_REQUEST_TOOLS_ITEM_VALUES!r}")
