from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="AssetSpec")


@_attrs_define
class AssetSpec:
    """
    Attributes:
        knowledge_bases (list[str] | Unset):
        skills (list[str] | Unset):
        notebooks (list[str] | Unset):
    """

    knowledge_bases: list[str] | Unset = UNSET
    skills: list[str] | Unset = UNSET
    notebooks: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        knowledge_bases: list[str] | Unset = UNSET
        if not isinstance(self.knowledge_bases, Unset):
            knowledge_bases = self.knowledge_bases

        skills: list[str] | Unset = UNSET
        if not isinstance(self.skills, Unset):
            skills = self.skills

        notebooks: list[str] | Unset = UNSET
        if not isinstance(self.notebooks, Unset):
            notebooks = self.notebooks

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if knowledge_bases is not UNSET:
            field_dict["knowledge_bases"] = knowledge_bases
        if skills is not UNSET:
            field_dict["skills"] = skills
        if notebooks is not UNSET:
            field_dict["notebooks"] = notebooks

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        knowledge_bases = cast(list[str], d.pop("knowledge_bases", UNSET))

        skills = cast(list[str], d.pop("skills", UNSET))

        notebooks = cast(list[str], d.pop("notebooks", UNSET))

        asset_spec = cls(
            knowledge_bases=knowledge_bases,
            skills=skills,
            notebooks=notebooks,
        )

        asset_spec.additional_properties = d
        return asset_spec

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
