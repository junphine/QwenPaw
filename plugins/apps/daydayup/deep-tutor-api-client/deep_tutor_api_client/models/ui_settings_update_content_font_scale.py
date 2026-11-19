from typing import Literal

UISettingsUpdateContentFontScale = Literal[90, 100, 110, 125, 150]

UI_SETTINGS_UPDATE_CONTENT_FONT_SCALE_VALUES: set[UISettingsUpdateContentFontScale] = {
    90,
    100,
    110,
    125,
    150,
}


def check_ui_settings_update_content_font_scale(value: int) -> UISettingsUpdateContentFontScale:
    if value in UI_SETTINGS_UPDATE_CONTENT_FONT_SCALE_VALUES:
        return value
    raise TypeError(f"Unexpected value {value!r}. Expected one of {UI_SETTINGS_UPDATE_CONTENT_FONT_SCALE_VALUES!r}")
