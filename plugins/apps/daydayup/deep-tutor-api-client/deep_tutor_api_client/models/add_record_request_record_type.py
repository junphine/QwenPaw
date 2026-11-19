from typing import Literal

AddRecordRequestRecordType = Literal[
    "chat", "co_writer", "question", "reading", "research", "solve", "tutorbot", "video_learning"
]

ADD_RECORD_REQUEST_RECORD_TYPE_VALUES: set[AddRecordRequestRecordType] = {
    "chat",
    "co_writer",
    "question",
    "reading",
    "research",
    "solve",
    "tutorbot",
    "video_learning",
}


def check_add_record_request_record_type(value: str) -> AddRecordRequestRecordType:
    if value in ADD_RECORD_REQUEST_RECORD_TYPE_VALUES:
        return value
    raise TypeError(f"Unexpected value {value!r}. Expected one of {ADD_RECORD_REQUEST_RECORD_TYPE_VALUES!r}")
