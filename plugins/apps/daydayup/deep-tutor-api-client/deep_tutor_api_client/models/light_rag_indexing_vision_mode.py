from typing import Literal

LightRagIndexingVisionMode = Literal["disabled", "enabled"]

LIGHT_RAG_INDEXING_VISION_MODE_VALUES: set[LightRagIndexingVisionMode] = {
    "disabled",
    "enabled",
}


def check_light_rag_indexing_vision_mode(value: str) -> LightRagIndexingVisionMode:
    if value in LIGHT_RAG_INDEXING_VISION_MODE_VALUES:
        return value
    raise TypeError(f"Unexpected value {value!r}. Expected one of {LIGHT_RAG_INDEXING_VISION_MODE_VALUES!r}")
