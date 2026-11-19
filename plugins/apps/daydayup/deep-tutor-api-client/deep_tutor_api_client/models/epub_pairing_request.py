from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="EpubPairingRequest")


@_attrs_define
class EpubPairingRequest:
    """
    Attributes:
        english_material_id (str):
        chinese_material_id (str):
    """

    english_material_id: str
    chinese_material_id: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        english_material_id = self.english_material_id

        chinese_material_id = self.chinese_material_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "english_material_id": english_material_id,
                "chinese_material_id": chinese_material_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        english_material_id = d.pop("english_material_id")

        chinese_material_id = d.pop("chinese_material_id")

        epub_pairing_request = cls(
            english_material_id=english_material_id,
            chinese_material_id=chinese_material_id,
        )

        epub_pairing_request.additional_properties = d
        return epub_pairing_request

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
