from typing import Literal

UISettingsUpdateResponseLanguageType0 = Literal[
    "ar", "de", "en", "es", "fr", "hi", "hu", "it", "ja", "ko", "ms", "pl", "pt", "ru", "tr", "uk", "vi", "zh", "zh-tw"
]

UI_SETTINGS_UPDATE_RESPONSE_LANGUAGE_TYPE_0_VALUES: set[UISettingsUpdateResponseLanguageType0] = {
    "ar",
    "de",
    "en",
    "es",
    "fr",
    "hi",
    "hu",
    "it",
    "ja",
    "ko",
    "ms",
    "pl",
    "pt",
    "ru",
    "tr",
    "uk",
    "vi",
    "zh",
    "zh-tw",
}


def check_ui_settings_update_response_language_type_0(value: str) -> UISettingsUpdateResponseLanguageType0:
    if value in UI_SETTINGS_UPDATE_RESPONSE_LANGUAGE_TYPE_0_VALUES:
        return value
    raise TypeError(
        f"Unexpected value {value!r}. Expected one of {UI_SETTINGS_UPDATE_RESPONSE_LANGUAGE_TYPE_0_VALUES!r}"
    )
