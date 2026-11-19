from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from ..models.learning_page_customization_hidden_features_item import (
    LearningPageCustomizationHiddenFeaturesItem,
    check_learning_page_customization_hidden_features_item,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="LearningPageCustomization")


@_attrs_define
class LearningPageCustomization:
    """
    Attributes:
        hidden_features (list[LearningPageCustomizationHiddenFeaturesItem] | Unset):
    """

    hidden_features: list[LearningPageCustomizationHiddenFeaturesItem] | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        hidden_features: list[str] | Unset = UNSET
        if not isinstance(self.hidden_features, Unset):
            hidden_features = []
            for hidden_features_item_data in self.hidden_features:
                hidden_features_item: str = hidden_features_item_data
                hidden_features.append(hidden_features_item)

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if hidden_features is not UNSET:
            field_dict["hidden_features"] = hidden_features

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        _hidden_features = d.pop("hidden_features", UNSET)
        hidden_features: list[LearningPageCustomizationHiddenFeaturesItem] | Unset = UNSET
        if _hidden_features is not UNSET:
            hidden_features = []
            for hidden_features_item_data in _hidden_features:
                hidden_features_item = check_learning_page_customization_hidden_features_item(hidden_features_item_data)

                hidden_features.append(hidden_features_item)

        learning_page_customization = cls(
            hidden_features=hidden_features,
        )

        return learning_page_customization
