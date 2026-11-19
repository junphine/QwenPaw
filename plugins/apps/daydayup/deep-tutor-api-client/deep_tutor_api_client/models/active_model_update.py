from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ActiveModelUpdate")


@_attrs_define
class ActiveModelUpdate:
    """Switch the globally-active model for a kind (llm / embedding).

    Attributes:
        kind (str):
        profile_id (str):
        model_id (str):
    """

    kind: str
    profile_id: str
    model_id: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        kind = self.kind

        profile_id = self.profile_id

        model_id = self.model_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "kind": kind,
                "profile_id": profile_id,
                "model_id": model_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        kind = d.pop("kind")

        profile_id = d.pop("profile_id")

        model_id = d.pop("model_id")

        active_model_update = cls(
            kind=kind,
            profile_id=profile_id,
            model_id=model_id,
        )

        active_model_update.additional_properties = d
        return active_model_update

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
