from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="SupportedFormats")


@_attrs_define
class SupportedFormats:
    """
    Attributes:
        extensions (list[str]):
        max_bytes (int):
        raw_view_extensions (list[str]):
    """

    extensions: list[str]
    max_bytes: int
    raw_view_extensions: list[str]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        extensions = self.extensions

        max_bytes = self.max_bytes

        raw_view_extensions = self.raw_view_extensions

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "extensions": extensions,
                "max_bytes": max_bytes,
                "raw_view_extensions": raw_view_extensions,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        extensions = cast(list[str], d.pop("extensions"))

        max_bytes = d.pop("max_bytes")

        raw_view_extensions = cast(list[str], d.pop("raw_view_extensions"))

        supported_formats = cls(
            extensions=extensions,
            max_bytes=max_bytes,
            raw_view_extensions=raw_view_extensions,
        )

        supported_formats.additional_properties = d
        return supported_formats

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
