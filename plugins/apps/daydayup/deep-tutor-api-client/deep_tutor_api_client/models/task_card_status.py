from typing import Literal

TaskCardStatus = Literal["doing", "done", "todo"]

TASK_CARD_STATUS_VALUES: set[TaskCardStatus] = {
    "doing",
    "done",
    "todo",
}


def check_task_card_status(value: str) -> TaskCardStatus:
    if value in TASK_CARD_STATUS_VALUES:
        return value
    raise TypeError(f"Unexpected value {value!r}. Expected one of {TASK_CARD_STATUS_VALUES!r}")
