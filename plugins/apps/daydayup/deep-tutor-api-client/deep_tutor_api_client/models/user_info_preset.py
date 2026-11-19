from typing import Literal

UserInfoPreset = Literal["custom", "learner", "standard"]

USER_INFO_PRESET_VALUES: set[UserInfoPreset] = {
    "custom",
    "learner",
    "standard",
}


def check_user_info_preset(value: str) -> UserInfoPreset:
    if value in USER_INFO_PRESET_VALUES:
        return value
    raise TypeError(f"Unexpected value {value!r}. Expected one of {USER_INFO_PRESET_VALUES!r}")
