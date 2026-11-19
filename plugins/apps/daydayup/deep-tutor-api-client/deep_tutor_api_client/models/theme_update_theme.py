from typing import Literal

ThemeUpdateTheme = Literal["dark", "glass", "light", "snow", "system"]

THEME_UPDATE_THEME_VALUES: set[ThemeUpdateTheme] = {
    "dark",
    "glass",
    "light",
    "snow",
    "system",
}


def check_theme_update_theme(value: str) -> ThemeUpdateTheme:
    if value in THEME_UPDATE_THEME_VALUES:
        return value
    raise TypeError(f"Unexpected value {value!r}. Expected one of {THEME_UPDATE_THEME_VALUES!r}")
