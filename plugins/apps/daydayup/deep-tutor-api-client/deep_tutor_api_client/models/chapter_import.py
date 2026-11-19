from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ChapterImport")


@_attrs_define
class ChapterImport:
    """
    Attributes:
        title (str):
        knowledge_points (list[str] | Unset):
    """

    title: str
    knowledge_points: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        title = self.title

        knowledge_points: list[str] | Unset = UNSET
        if not isinstance(self.knowledge_points, Unset):
            knowledge_points = self.knowledge_points

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "title": title,
            }
        )
        if knowledge_points is not UNSET:
            field_dict["knowledge_points"] = knowledge_points

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        title = d.pop("title")

        knowledge_points = cast(list[str], d.pop("knowledge_points", UNSET))

        chapter_import = cls(
            title=title,
            knowledge_points=knowledge_points,
        )

        chapter_import.additional_properties = d
        return chapter_import

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
