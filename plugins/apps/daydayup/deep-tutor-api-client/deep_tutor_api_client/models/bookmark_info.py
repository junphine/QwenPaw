from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="BookmarkInfo")


@_attrs_define
class BookmarkInfo:
    """
    Attributes:
        locator (int):
        bookmark_id (str):
        label (str | Unset):  Default: ''.
        source_anchor (str | Unset):  Default: ''.
        created_at (float | Unset):  Default: 0.0.
    """

    locator: int
    bookmark_id: str
    label: str | Unset = ""
    source_anchor: str | Unset = ""
    created_at: float | Unset = 0.0
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        locator = self.locator

        bookmark_id = self.bookmark_id

        label = self.label

        source_anchor = self.source_anchor

        created_at = self.created_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "locator": locator,
                "bookmark_id": bookmark_id,
            }
        )
        if label is not UNSET:
            field_dict["label"] = label
        if source_anchor is not UNSET:
            field_dict["source_anchor"] = source_anchor
        if created_at is not UNSET:
            field_dict["created_at"] = created_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        locator = d.pop("locator")

        bookmark_id = d.pop("bookmark_id")

        label = d.pop("label", UNSET)

        source_anchor = d.pop("source_anchor", UNSET)

        created_at = d.pop("created_at", UNSET)

        bookmark_info = cls(
            locator=locator,
            bookmark_id=bookmark_id,
            label=label,
            source_anchor=source_anchor,
            created_at=created_at,
        )

        bookmark_info.additional_properties = d
        return bookmark_info

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
