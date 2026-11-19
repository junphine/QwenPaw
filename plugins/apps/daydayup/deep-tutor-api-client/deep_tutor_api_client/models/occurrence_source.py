from typing import Literal

OccurrenceSource = Literal["dito", "import", "user"]

OCCURRENCE_SOURCE_VALUES: set[OccurrenceSource] = {
    "dito",
    "import",
    "user",
}


def check_occurrence_source(value: str) -> OccurrenceSource:
    if value in OCCURRENCE_SOURCE_VALUES:
        return value
    raise TypeError(f"Unexpected value {value!r}. Expected one of {OCCURRENCE_SOURCE_VALUES!r}")
