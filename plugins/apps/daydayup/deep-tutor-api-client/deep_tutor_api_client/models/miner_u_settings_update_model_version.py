from typing import Literal

MinerUSettingsUpdateModelVersion = Literal["pipeline", "vlm"]

MINER_U_SETTINGS_UPDATE_MODEL_VERSION_VALUES: set[MinerUSettingsUpdateModelVersion] = {
    "pipeline",
    "vlm",
}


def check_miner_u_settings_update_model_version(value: str) -> MinerUSettingsUpdateModelVersion:
    if value in MINER_U_SETTINGS_UPDATE_MODEL_VERSION_VALUES:
        return value
    raise TypeError(f"Unexpected value {value!r}. Expected one of {MINER_U_SETTINGS_UPDATE_MODEL_VERSION_VALUES!r}")
