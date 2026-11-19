from typing import Literal

UpdateCardStatusType0 = Literal["doing", "done", "todo"]

UPDATE_CARD_STATUS_TYPE_0_VALUES: set[UpdateCardStatusType0] = {
    "doing",
    "done",
    "todo",
}


def check_update_card_status_type_0(value: str) -> UpdateCardStatusType0:
    if value in UPDATE_CARD_STATUS_TYPE_0_VALUES:
        return value
    raise TypeError(f"Unexpected value {value!r}. Expected one of {UPDATE_CARD_STATUS_TYPE_0_VALUES!r}")
