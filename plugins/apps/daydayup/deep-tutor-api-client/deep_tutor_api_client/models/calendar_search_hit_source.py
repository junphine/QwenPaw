from typing import Literal

CalendarSearchHitSource = Literal["dito", "import", "user"]

CALENDAR_SEARCH_HIT_SOURCE_VALUES: set[CalendarSearchHitSource] = {
    "dito",
    "import",
    "user",
}


def check_calendar_search_hit_source(value: str) -> CalendarSearchHitSource:
    if value in CALENDAR_SEARCH_HIT_SOURCE_VALUES:
        return value
    raise TypeError(f"Unexpected value {value!r}. Expected one of {CALENDAR_SEARCH_HIT_SOURCE_VALUES!r}")
