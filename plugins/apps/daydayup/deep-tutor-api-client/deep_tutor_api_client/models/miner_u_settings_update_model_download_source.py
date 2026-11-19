from typing import Literal

MinerUSettingsUpdateModelDownloadSource = Literal["huggingface", "modelscope"]

MINER_U_SETTINGS_UPDATE_MODEL_DOWNLOAD_SOURCE_VALUES: set[MinerUSettingsUpdateModelDownloadSource] = {
    "huggingface",
    "modelscope",
}


def check_miner_u_settings_update_model_download_source(value: str) -> MinerUSettingsUpdateModelDownloadSource:
    if value in MINER_U_SETTINGS_UPDATE_MODEL_DOWNLOAD_SOURCE_VALUES:
        return value
    raise TypeError(
        f"Unexpected value {value!r}. Expected one of {MINER_U_SETTINGS_UPDATE_MODEL_DOWNLOAD_SOURCE_VALUES!r}"
    )
