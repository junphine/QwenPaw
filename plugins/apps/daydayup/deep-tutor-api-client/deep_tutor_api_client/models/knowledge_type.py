from typing import Literal

KnowledgeType = Literal["concept", "design", "memory", "procedure"]

KNOWLEDGE_TYPE_VALUES: set[KnowledgeType] = {
    "concept",
    "design",
    "memory",
    "procedure",
}


def check_knowledge_type(value: str) -> KnowledgeType:
    if value in KNOWLEDGE_TYPE_VALUES:
        return value
    raise TypeError(f"Unexpected value {value!r}. Expected one of {KNOWLEDGE_TYPE_VALUES!r}")
