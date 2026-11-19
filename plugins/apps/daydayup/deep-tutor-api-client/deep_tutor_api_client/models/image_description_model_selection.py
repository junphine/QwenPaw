from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="ImageDescriptionModelSelection")


@_attrs_define
class ImageDescriptionModelSelection:
    """Reference a configured vision model without changing the chat default.

    Attributes:
        profile_id (str):
        model_id (str):
    """

    profile_id: str
    model_id: str

    def to_dict(self) -> dict[str, Any]:
        profile_id = self.profile_id

        model_id = self.model_id

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "profile_id": profile_id,
                "model_id": model_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        profile_id = d.pop("profile_id")

        model_id = d.pop("model_id")

        image_description_model_selection = cls(
            profile_id=profile_id,
            model_id=model_id,
        )

        return image_description_model_selection
