from typing import Literal

DisplaySettingsContentFontScale = Literal[90, 100, 110, 125, 150]

DISPLAY_SETTINGS_CONTENT_FONT_SCALE_VALUES: set[DisplaySettingsContentFontScale] = {
    90,
    100,
    110,
    125,
    150,
}


def check_display_settings_content_font_scale(value: int) -> DisplaySettingsContentFontScale:
    if value in DISPLAY_SETTINGS_CONTENT_FONT_SCALE_VALUES:
        return value
    raise TypeError(f"Unexpected value {value!r}. Expected one of {DISPLAY_SETTINGS_CONTENT_FONT_SCALE_VALUES!r}")
