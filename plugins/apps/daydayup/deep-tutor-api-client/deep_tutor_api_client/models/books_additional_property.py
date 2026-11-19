from typing import Literal

BooksAdditionalProperty = Literal["edit", "none", "read"]

BOOKS_ADDITIONAL_PROPERTY_VALUES: set[BooksAdditionalProperty] = {
    "edit",
    "none",
    "read",
}


def check_books_additional_property(value: str) -> BooksAdditionalProperty:
    if value in BOOKS_ADDITIONAL_PROPERTY_VALUES:
        return value
    raise TypeError(f"Unexpected value {value!r}. Expected one of {BOOKS_ADDITIONAL_PROPERTY_VALUES!r}")
