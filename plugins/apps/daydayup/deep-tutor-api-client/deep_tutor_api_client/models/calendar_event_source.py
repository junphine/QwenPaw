from typing import Literal

CalendarEventSource = Literal["dito", "import", "user"]

CALENDAR_EVENT_SOURCE_VALUES: set[CalendarEventSource] = {
    "dito",
    "import",
    "user",
}


def check_calendar_event_source(value: str) -> CalendarEventSource:
    if value in CALENDAR_EVENT_SOURCE_VALUES:
        return value
    raise TypeError(f"Unexpected value {value!r}. Expected one of {CALENDAR_EVENT_SOURCE_VALUES!r}")
