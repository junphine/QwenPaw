from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="SupportedFileTypesInfo")


@_attrs_define
class SupportedFileTypesInfo:
    """Upload constraints exposed to the web client.

    Attributes:
        extensions (list[str]):
        accept (str):
        max_file_size_bytes (int):
        allow_any_extension (bool | Unset):  Default: False.
    """

    extensions: list[str]
    accept: str
    max_file_size_bytes: int
    allow_any_extension: bool | Unset = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        extensions = self.extensions

        accept = self.accept

        max_file_size_bytes = self.max_file_size_bytes

        allow_any_extension = self.allow_any_extension

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "extensions": extensions,
                "accept": accept,
                "max_file_size_bytes": max_file_size_bytes,
            }
        )
        if allow_any_extension is not UNSET:
            field_dict["allow_any_extension"] = allow_any_extension

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        extensions = cast(list[str], d.pop("extensions"))

        accept = d.pop("accept")

        max_file_size_bytes = d.pop("max_file_size_bytes")

        allow_any_extension = d.pop("allow_any_extension", UNSET)

        supported_file_types_info = cls(
            extensions=extensions,
            accept=accept,
            max_file_size_bytes=max_file_size_bytes,
            allow_any_extension=allow_any_extension,
        )

        supported_file_types_info.additional_properties = d
        return supported_file_types_info

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
