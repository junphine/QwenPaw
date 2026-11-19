from typing import Literal

DisplaySettingsContentLineSpacing = Literal["compact", "normal", "relaxed"]

DISPLAY_SETTINGS_CONTENT_LINE_SPACING_VALUES: set[DisplaySettingsContentLineSpacing] = {
    "compact",
    "normal",
    "relaxed",
}


def check_display_settings_content_line_spacing(value: str) -> DisplaySettingsContentLineSpacing:
    if value in DISPLAY_SETTINGS_CONTENT_LINE_SPACING_VALUES:
        return value
    raise TypeError(f"Unexpected value {value!r}. Expected one of {DISPLAY_SETTINGS_CONTENT_LINE_SPACING_VALUES!r}")
