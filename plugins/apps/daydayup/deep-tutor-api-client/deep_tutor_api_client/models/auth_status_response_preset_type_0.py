from typing import Literal

AuthStatusResponsePresetType0 = Literal["custom", "learner", "standard"]

AUTH_STATUS_RESPONSE_PRESET_TYPE_0_VALUES: set[AuthStatusResponsePresetType0] = {
    "custom",
    "learner",
    "standard",
}


def check_auth_status_response_preset_type_0(value: str) -> AuthStatusResponsePresetType0:
    if value in AUTH_STATUS_RESPONSE_PRESET_TYPE_0_VALUES:
        return value
    raise TypeError(f"Unexpected value {value!r}. Expected one of {AUTH_STATUS_RESPONSE_PRESET_TYPE_0_VALUES!r}")
