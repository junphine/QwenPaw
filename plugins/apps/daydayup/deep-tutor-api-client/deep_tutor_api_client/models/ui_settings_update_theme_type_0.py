from typing import Literal

UISettingsUpdateThemeType0 = Literal["dark", "glass", "light", "snow", "system"]

UI_SETTINGS_UPDATE_THEME_TYPE_0_VALUES: set[UISettingsUpdateThemeType0] = {
    "dark",
    "glass",
    "light",
    "snow",
    "system",
}


def check_ui_settings_update_theme_type_0(value: str) -> UISettingsUpdateThemeType0:
    if value in UI_SETTINGS_UPDATE_THEME_TYPE_0_VALUES:
        return value
    raise TypeError(f"Unexpected value {value!r}. Expected one of {UI_SETTINGS_UPDATE_THEME_TYPE_0_VALUES!r}")
