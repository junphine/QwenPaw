from typing import Literal

LanguageUpdateLanguage = Literal["de", "en", "fr", "hu", "it", "ja", "pl", "pt", "tr", "uk", "vi", "zh"]

LANGUAGE_UPDATE_LANGUAGE_VALUES: set[LanguageUpdateLanguage] = {
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


def check_language_update_language(value: str) -> LanguageUpdateLanguage:
    if value in LANGUAGE_UPDATE_LANGUAGE_VALUES:
        return value
    raise TypeError(f"Unexpected value {value!r}. Expected one of {LANGUAGE_UPDATE_LANGUAGE_VALUES!r}")
