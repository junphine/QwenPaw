from typing import Literal

MinerUSettingsUpdateMode = Literal["cloud", "local"]

MINER_U_SETTINGS_UPDATE_MODE_VALUES: set[MinerUSettingsUpdateMode] = {
    "cloud",
    "local",
}


def check_miner_u_settings_update_mode(value: str) -> MinerUSettingsUpdateMode:
    if value in MINER_U_SETTINGS_UPDATE_MODE_VALUES:
        return value
    raise TypeError(f"Unexpected value {value!r}. Expected one of {MINER_U_SETTINGS_UPDATE_MODE_VALUES!r}")
