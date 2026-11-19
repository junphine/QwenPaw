from typing import Literal

TopicSourceKind = Literal[
    "book", "chat", "cowriter", "file", "goal", "knowledge_base", "notebook", "partner_group", "question_bank"
]

TOPIC_SOURCE_KIND_VALUES: set[TopicSourceKind] = {
    "book",
    "chat",
    "cowriter",
    "file",
    "goal",
    "knowledge_base",
    "notebook",
    "partner_group",
    "question_bank",
}


def check_topic_source_kind(value: str) -> TopicSourceKind:
    if value in TOPIC_SOURCE_KIND_VALUES:
        return value
    raise TypeError(f"Unexpected value {value!r}. Expected one of {TOPIC_SOURCE_KIND_VALUES!r}")
