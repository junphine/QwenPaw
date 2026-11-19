from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from .. import types
from ..types import UNSET, Unset

T = TypeVar("T", bound="BodyLibraryAdd")


@_attrs_define
class BodyLibraryAdd:
    """
    Attributes:
        filename (str): Original filename
        file (str): Raw file bytes
        mime_type (str | Unset):  Default: ''.
    """

    filename: str
    file: str
    mime_type: str | Unset = ""
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        filename = self.filename

        file = self.file

        mime_type = self.mime_type

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "filename": filename,
                "file": file,
            }
        )
        if mime_type is not UNSET:
            field_dict["mime_type"] = mime_type

        return field_dict

    def to_multipart(self) -> types.RequestFiles:
        files: types.RequestFiles = []

        files.append(("filename", (None, str(self.filename).encode(), "text/plain")))

        files.append(("file", (None, str(self.file).encode(), "text/plain")))

        if not isinstance(self.mime_type, Unset):
            files.append(("mime_type", (None, str(self.mime_type).encode(), "text/plain")))

        for prop_name, prop in self.additional_properties.items():
            files.append((prop_name, (None, str(prop).encode(), "text/plain")))

        return files

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        filename = d.pop("filename")

        file = d.pop("file")

        mime_type = d.pop("mime_type", UNSET)

        body_library_add = cls(
            filename=filename,
            file=file,
            mime_type=mime_type,
        )

        body_library_add.additional_properties = d
        return body_library_add

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
