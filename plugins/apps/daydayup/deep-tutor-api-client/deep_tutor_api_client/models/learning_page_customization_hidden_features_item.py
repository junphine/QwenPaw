from typing import Literal

LearningPageCustomizationHiddenFeaturesItem = Literal["books", "mastery", "practice", "reading"]

LEARNING_PAGE_CUSTOMIZATION_HIDDEN_FEATURES_ITEM_VALUES: set[LearningPageCustomizationHiddenFeaturesItem] = {
    "books",
    "mastery",
    "practice",
    "reading",
}


def check_learning_page_customization_hidden_features_item(value: str) -> LearningPageCustomizationHiddenFeaturesItem:
    if value in LEARNING_PAGE_CUSTOMIZATION_HIDDEN_FEATURES_ITEM_VALUES:
        return value
    raise TypeError(
        f"Unexpected value {value!r}. Expected one of {LEARNING_PAGE_CUSTOMIZATION_HIDDEN_FEATURES_ITEM_VALUES!r}"
    )
