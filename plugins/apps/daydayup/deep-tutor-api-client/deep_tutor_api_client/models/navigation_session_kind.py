from typing import Literal

NavigationSessionKind = Literal["group", "partner"]

NAVIGATION_SESSION_KIND_VALUES: set[NavigationSessionKind] = {
    "group",
    "partner",
}


def check_navigation_session_kind(value: str) -> NavigationSessionKind:
    if value in NAVIGATION_SESSION_KIND_VALUES:
        return value
    raise TypeError(f"Unexpected value {value!r}. Expected one of {NAVIGATION_SESSION_KIND_VALUES!r}")
