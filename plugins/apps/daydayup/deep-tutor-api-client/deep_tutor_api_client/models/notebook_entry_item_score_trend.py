from typing import Literal

NotebookEntryItemScoreTrend = Literal["declined", "improved", "new", "unchanged"]

NOTEBOOK_ENTRY_ITEM_SCORE_TREND_VALUES: set[NotebookEntryItemScoreTrend] = {
    "declined",
    "improved",
    "new",
    "unchanged",
}


def check_notebook_entry_item_score_trend(value: str) -> NotebookEntryItemScoreTrend:
    if value in NOTEBOOK_ENTRY_ITEM_SCORE_TREND_VALUES:
        return value
    raise TypeError(f"Unexpected value {value!r}. Expected one of {NOTEBOOK_ENTRY_ITEM_SCORE_TREND_VALUES!r}")
