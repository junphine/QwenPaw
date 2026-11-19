from typing import Literal

LightRagRoleModelMode = Literal["inherit", "model"]

LIGHT_RAG_ROLE_MODEL_MODE_VALUES: set[LightRagRoleModelMode] = {
    "inherit",
    "model",
}


def check_light_rag_role_model_mode(value: str) -> LightRagRoleModelMode:
    if value in LIGHT_RAG_ROLE_MODEL_MODE_VALUES:
        return value
    raise TypeError(f"Unexpected value {value!r}. Expected one of {LIGHT_RAG_ROLE_MODEL_MODE_VALUES!r}")
