from typing import Literal

LightRagRoleModelReasoningEffortType0 = Literal["adaptive", "high", "low", "max", "medium", "minimal", "none", "xhigh"]

LIGHT_RAG_ROLE_MODEL_REASONING_EFFORT_TYPE_0_VALUES: set[LightRagRoleModelReasoningEffortType0] = {
    "adaptive",
    "high",
    "low",
    "max",
    "medium",
    "minimal",
    "none",
    "xhigh",
}


def check_light_rag_role_model_reasoning_effort_type_0(value: str) -> LightRagRoleModelReasoningEffortType0:
    if value in LIGHT_RAG_ROLE_MODEL_REASONING_EFFORT_TYPE_0_VALUES:
        return value
    raise TypeError(
        f"Unexpected value {value!r}. Expected one of {LIGHT_RAG_ROLE_MODEL_REASONING_EFFORT_TYPE_0_VALUES!r}"
    )
