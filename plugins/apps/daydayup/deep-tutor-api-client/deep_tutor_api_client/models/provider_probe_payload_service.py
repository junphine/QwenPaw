from typing import Literal

ProviderProbePayloadService = Literal["embedding", "imagegen", "llm", "search", "stt", "task", "tts", "videogen"]

PROVIDER_PROBE_PAYLOAD_SERVICE_VALUES: set[ProviderProbePayloadService] = {
    "embedding",
    "imagegen",
    "llm",
    "search",
    "stt",
    "task",
    "tts",
    "videogen",
}


def check_provider_probe_payload_service(value: str) -> ProviderProbePayloadService:
    if value in PROVIDER_PROBE_PAYLOAD_SERVICE_VALUES:
        return value
    raise TypeError(f"Unexpected value {value!r}. Expected one of {PROVIDER_PROBE_PAYLOAD_SERVICE_VALUES!r}")
