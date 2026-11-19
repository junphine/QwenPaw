from typing import Literal

LightRagVisionModelReasoningEffortType0 = Literal[
    "adaptive", "high", "low", "max", "medium", "minimal", "none", "xhigh"
]

LIGHT_RAG_VISION_MODEL_REASONING_EFFORT_TYPE_0_VALUES: set[LightRagVisionModelReasoningEffortType0] = {
    "adaptive",
    "high",
    "low",
    "max",
    "medium",
    "minimal",
    "none",
    "xhigh",
}


def check_light_rag_vision_model_reasoning_effort_type_0(value: str) -> LightRagVisionModelReasoningEffortType0:
    if value in LIGHT_RAG_VISION_MODEL_REASONING_EFFORT_TYPE_0_VALUES:
        return value
    raise TypeError(
        f"Unexpected value {value!r}. Expected one of {LIGHT_RAG_VISION_MODEL_REASONING_EFFORT_TYPE_0_VALUES!r}"
    )
