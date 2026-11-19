from typing import Literal

ProviderEditPayloadService = Literal["embedding", "imagegen", "llm", "search", "stt", "task", "tts", "videogen"]

PROVIDER_EDIT_PAYLOAD_SERVICE_VALUES: set[ProviderEditPayloadService] = {
    "embedding",
    "imagegen",
    "llm",
    "search",
    "stt",
    "task",
    "tts",
    "videogen",
}


def check_provider_edit_payload_service(value: str) -> ProviderEditPayloadService:
    if value in PROVIDER_EDIT_PAYLOAD_SERVICE_VALUES:
        return value
    raise TypeError(f"Unexpected value {value!r}. Expected one of {PROVIDER_EDIT_PAYLOAD_SERVICE_VALUES!r}")
