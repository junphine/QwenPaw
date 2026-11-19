from typing import Literal

FetchModelsPayloadService = Literal["llm", "task"]

FETCH_MODELS_PAYLOAD_SERVICE_VALUES: set[FetchModelsPayloadService] = {
    "llm",
    "task",
}


def check_fetch_models_payload_service(value: str) -> FetchModelsPayloadService:
    if value in FETCH_MODELS_PAYLOAD_SERVICE_VALUES:
        return value
    raise TypeError(f"Unexpected value {value!r}. Expected one of {FETCH_MODELS_PAYLOAD_SERVICE_VALUES!r}")
