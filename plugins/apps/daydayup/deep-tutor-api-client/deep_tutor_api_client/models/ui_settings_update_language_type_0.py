from typing import Literal

UISettingsUpdateLanguageType0 = Literal["de", "en", "fr", "hu", "it", "ja", "pl", "pt", "tr", "uk", "vi", "zh"]

UI_SETTINGS_UPDATE_LANGUAGE_TYPE_0_VALUES: set[UISettingsUpdateLanguageType0] = {
    "de",
    "en",
    "fr",
    "hu",
    "it",
    "ja",
    "pl",
    "pt",
    "tr",
    "uk",
    "vi",
    "zh",
}


def check_ui_settings_update_language_type_0(value: str) -> UISettingsUpdateLanguageType0:
    if value in UI_SETTINGS_UPDATE_LANGUAGE_TYPE_0_VALUES:
        return value
    raise TypeError(f"Unexpected value {value!r}. Expected one of {UI_SETTINGS_UPDATE_LANGUAGE_TYPE_0_VALUES!r}")
