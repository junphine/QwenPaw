from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="QuestionBankMaterial")


@_attrs_define
class QuestionBankMaterial:
    """
    Attributes:
        source (str):
        material_id (str):
        material_title (str):
        entry_count (int):
        unresolved_count (int):
    """

    source: str
    material_id: str
    material_title: str
    entry_count: int
    unresolved_count: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        source = self.source

        material_id = self.material_id

        material_title = self.material_title

        entry_count = self.entry_count

        unresolved_count = self.unresolved_count

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "source": source,
                "material_id": material_id,
                "material_title": material_title,
                "entry_count": entry_count,
                "unresolved_count": unresolved_count,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        source = d.pop("source")

        material_id = d.pop("material_id")

        material_title = d.pop("material_title")

        entry_count = d.pop("entry_count")

        unresolved_count = d.pop("unresolved_count")

        question_bank_material = cls(
            source=source,
            material_id=material_id,
            material_title=material_title,
            entry_count=entry_count,
            unresolved_count=unresolved_count,
        )

        question_bank_material.additional_properties = d
        return question_bank_material

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
