from typing import Literal

MinerUModelDownloadPayloadSource = Literal["huggingface", "modelscope"]

MINER_U_MODEL_DOWNLOAD_PAYLOAD_SOURCE_VALUES: set[MinerUModelDownloadPayloadSource] = {
    "huggingface",
    "modelscope",
}


def check_miner_u_model_download_payload_source(value: str) -> MinerUModelDownloadPayloadSource:
    if value in MINER_U_MODEL_DOWNLOAD_PAYLOAD_SOURCE_VALUES:
        return value
    raise TypeError(f"Unexpected value {value!r}. Expected one of {MINER_U_MODEL_DOWNLOAD_PAYLOAD_SOURCE_VALUES!r}")
