from typing import Literal

ReadingActivityRecordResultType = Literal["browser_speech", "card", "feedback", "quiz"]

READING_ACTIVITY_RECORD_RESULT_TYPE_VALUES: set[ReadingActivityRecordResultType] = {
    "browser_speech",
    "card",
    "feedback",
    "quiz",
}


def check_reading_activity_record_result_type(value: str) -> ReadingActivityRecordResultType:
    if value in READING_ACTIVITY_RECORD_RESULT_TYPE_VALUES:
        return value
    raise TypeError(f"Unexpected value {value!r}. Expected one of {READING_ACTIVITY_RECORD_RESULT_TYPE_VALUES!r}")
