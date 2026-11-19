from typing import Literal

AdminCreateUserRequestPreset = Literal["custom", "learner", "standard"]

ADMIN_CREATE_USER_REQUEST_PRESET_VALUES: set[AdminCreateUserRequestPreset] = {
    "custom",
    "learner",
    "standard",
}


def check_admin_create_user_request_preset(value: str) -> AdminCreateUserRequestPreset:
    if value in ADMIN_CREATE_USER_REQUEST_PRESET_VALUES:
        return value
    raise TypeError(f"Unexpected value {value!r}. Expected one of {ADMIN_CREATE_USER_REQUEST_PRESET_VALUES!r}")
