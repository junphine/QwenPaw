from typing import Literal

RegistryEditPayloadServiceType0 = Literal["embedding", "imagegen", "llm", "search", "stt", "task", "tts", "videogen"]

REGISTRY_EDIT_PAYLOAD_SERVICE_TYPE_0_VALUES: set[RegistryEditPayloadServiceType0] = {
    "embedding",
    "imagegen",
    "llm",
    "search",
    "stt",
    "task",
    "tts",
    "videogen",
}


def check_registry_edit_payload_service_type_0(value: str) -> RegistryEditPayloadServiceType0:
    if value in REGISTRY_EDIT_PAYLOAD_SERVICE_TYPE_0_VALUES:
        return value
    raise TypeError(f"Unexpected value {value!r}. Expected one of {REGISTRY_EDIT_PAYLOAD_SERVICE_TYPE_0_VALUES!r}")
