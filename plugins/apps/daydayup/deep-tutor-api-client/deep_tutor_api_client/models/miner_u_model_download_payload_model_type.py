from typing import Literal

MinerUModelDownloadPayloadModelType = Literal["all", "pipeline", "vlm"]

MINER_U_MODEL_DOWNLOAD_PAYLOAD_MODEL_TYPE_VALUES: set[MinerUModelDownloadPayloadModelType] = {
    "all",
    "pipeline",
    "vlm",
}


def check_miner_u_model_download_payload_model_type(value: str) -> MinerUModelDownloadPayloadModelType:
    if value in MINER_U_MODEL_DOWNLOAD_PAYLOAD_MODEL_TYPE_VALUES:
        return value
    raise TypeError(f"Unexpected value {value!r}. Expected one of {MINER_U_MODEL_DOWNLOAD_PAYLOAD_MODEL_TYPE_VALUES!r}")
