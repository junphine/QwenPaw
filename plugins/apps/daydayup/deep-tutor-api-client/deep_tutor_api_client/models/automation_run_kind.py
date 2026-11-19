from typing import Literal

AutomationRunKind = Literal["at", "cron", "every"]

AUTOMATION_RUN_KIND_VALUES: set[AutomationRunKind] = {
    "at",
    "cron",
    "every",
}


def check_automation_run_kind(value: str) -> AutomationRunKind:
    if value in AUTOMATION_RUN_KIND_VALUES:
        return value
    raise TypeError(f"Unexpected value {value!r}. Expected one of {AUTOMATION_RUN_KIND_VALUES!r}")
