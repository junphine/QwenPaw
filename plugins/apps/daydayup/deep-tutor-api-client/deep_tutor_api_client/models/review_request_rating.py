from typing import Literal

ReviewRequestRating = Literal["again", "easy", "good", "hard"]

REVIEW_REQUEST_RATING_VALUES: set[ReviewRequestRating] = {
    "again",
    "easy",
    "good",
    "hard",
}


def check_review_request_rating(value: str) -> ReviewRequestRating:
    if value in REVIEW_REQUEST_RATING_VALUES:
        return value
    raise TypeError(f"Unexpected value {value!r}. Expected one of {REVIEW_REQUEST_RATING_VALUES!r}")
