from typing import Literal

SoulSpecSource = Literal["custom", "default", "library", "persona"]

SOUL_SPEC_SOURCE_VALUES: set[SoulSpecSource] = {
    "custom",
    "default",
    "library",
    "persona",
}


def check_soul_spec_source(value: str) -> SoulSpecSource:
    if value in SOUL_SPEC_SOURCE_VALUES:
        return value
    raise TypeError(f"Unexpected value {value!r}. Expected one of {SOUL_SPEC_SOURCE_VALUES!r}")
