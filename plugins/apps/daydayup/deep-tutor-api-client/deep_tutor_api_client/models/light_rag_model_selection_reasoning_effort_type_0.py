from typing import Literal

LightRagModelSelectionReasoningEffortType0 = Literal[
    "adaptive", "high", "low", "max", "medium", "minimal", "none", "xhigh"
]

LIGHT_RAG_MODEL_SELECTION_REASONING_EFFORT_TYPE_0_VALUES: set[LightRagModelSelectionReasoningEffortType0] = {
    "adaptive",
    "high",
    "low",
    "max",
    "medium",
    "minimal",
    "none",
    "xhigh",
}


def check_light_rag_model_selection_reasoning_effort_type_0(value: str) -> LightRagModelSelectionReasoningEffortType0:
    if value in LIGHT_RAG_MODEL_SELECTION_REASONING_EFFORT_TYPE_0_VALUES:
        return value
    raise TypeError(
        f"Unexpected value {value!r}. Expected one of {LIGHT_RAG_MODEL_SELECTION_REASONING_EFFORT_TYPE_0_VALUES!r}"
    )
