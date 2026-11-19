from typing import Literal

LightRagVisionModelMode = Literal["disabled", "inherit", "model"]

LIGHT_RAG_VISION_MODEL_MODE_VALUES: set[LightRagVisionModelMode] = {
    "disabled",
    "inherit",
    "model",
}


def check_light_rag_vision_model_mode(value: str) -> LightRagVisionModelMode:
    if value in LIGHT_RAG_VISION_MODEL_MODE_VALUES:
        return value
    raise TypeError(f"Unexpected value {value!r}. Expected one of {LIGHT_RAG_VISION_MODEL_MODE_VALUES!r}")
