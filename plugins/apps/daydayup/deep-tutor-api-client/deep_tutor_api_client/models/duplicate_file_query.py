from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="DuplicateFileQuery")


@_attrs_define
class DuplicateFileQuery:
    """
    Attributes:
        filename (str | Unset):  Default: ''.
        content_id (str | Unset):  Default: ''.
        size_bytes (int | Unset):  Default: 0.
        mime (str | Unset):  Default: ''.
    """

    filename: str | Unset = ""
    content_id: str | Unset = ""
    size_bytes: int | Unset = 0
    mime: str | Unset = ""
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        filename = self.filename

        content_id = self.content_id

        size_bytes = self.size_bytes

        mime = self.mime

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if filename is not UNSET:
            field_dict["filename"] = filename
        if content_id is not UNSET:
            field_dict["content_id"] = content_id
        if size_bytes is not UNSET:
            field_dict["size_bytes"] = size_bytes
        if mime is not UNSET:
            field_dict["mime"] = mime

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        filename = d.pop("filename", UNSET)

        content_id = d.pop("content_id", UNSET)

        size_bytes = d.pop("size_bytes", UNSET)

        mime = d.pop("mime", UNSET)

        duplicate_file_query = cls(
            filename=filename,
            content_id=content_id,
            size_bytes=size_bytes,
            mime=mime,
        )

        duplicate_file_query.additional_properties = d
        return duplicate_file_query

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
