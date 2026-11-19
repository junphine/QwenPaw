from typing import Literal

UISettingsUpdateContentLineSpacing = Literal["compact", "normal", "relaxed"]

UI_SETTINGS_UPDATE_CONTENT_LINE_SPACING_VALUES: set[UISettingsUpdateContentLineSpacing] = {
    "compact",
    "normal",
    "relaxed",
}


def check_ui_settings_update_content_line_spacing(value: str) -> UISettingsUpdateContentLineSpacing:
    if value in UI_SETTINGS_UPDATE_CONTENT_LINE_SPACING_VALUES:
        return value
    raise TypeError(f"Unexpected value {value!r}. Expected one of {UI_SETTINGS_UPDATE_CONTENT_LINE_SPACING_VALUES!r}")
