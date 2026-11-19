from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="BookmarkPayload")


@_attrs_define
class BookmarkPayload:
    """
    Attributes:
        locator (int):
        label (str | Unset):  Default: ''.
        source_anchor (str | Unset):  Default: ''.
    """

    locator: int
    label: str | Unset = ""
    source_anchor: str | Unset = ""
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        locator = self.locator

        label = self.label

        source_anchor = self.source_anchor

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "locator": locator,
            }
        )
        if label is not UNSET:
            field_dict["label"] = label
        if source_anchor is not UNSET:
            field_dict["source_anchor"] = source_anchor

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        locator = d.pop("locator")

        label = d.pop("label", UNSET)

        source_anchor = d.pop("source_anchor", UNSET)

        bookmark_payload = cls(
            locator=locator,
            label=label,
            source_anchor=source_anchor,
        )

        bookmark_payload.additional_properties = d
        return bookmark_payload

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
