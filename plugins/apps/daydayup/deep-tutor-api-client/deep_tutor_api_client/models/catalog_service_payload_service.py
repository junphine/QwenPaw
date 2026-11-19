from typing import Literal

CatalogServicePayloadService = Literal["embedding", "imagegen", "llm", "search", "stt", "task", "tts", "videogen"]

CATALOG_SERVICE_PAYLOAD_SERVICE_VALUES: set[CatalogServicePayloadService] = {
    "embedding",
    "imagegen",
    "llm",
    "search",
    "stt",
    "task",
    "tts",
    "videogen",
}


def check_catalog_service_payload_service(value: str) -> CatalogServicePayloadService:
    if value in CATALOG_SERVICE_PAYLOAD_SERVICE_VALUES:
        return value
    raise TypeError(f"Unexpected value {value!r}. Expected one of {CATALOG_SERVICE_PAYLOAD_SERVICE_VALUES!r}")
