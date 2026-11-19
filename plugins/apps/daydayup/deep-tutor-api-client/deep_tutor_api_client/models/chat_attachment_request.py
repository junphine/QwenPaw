from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ChatAttachmentRequest")


@_attrs_define
class ChatAttachmentRequest:
    """
    Attributes:
        type_ (str | Unset):  Default: 'file'.
        url (str | Unset):  Default: ''.
        base64 (str | Unset):  Default: ''.
        filename (str | Unset):  Default: ''.
        mime_type (str | Unset):  Default: ''.
    """

    type_: str | Unset = "file"
    url: str | Unset = ""
    base64: str | Unset = ""
    filename: str | Unset = ""
    mime_type: str | Unset = ""
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_

        url = self.url

        base64 = self.base64

        filename = self.filename

        mime_type = self.mime_type

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if type_ is not UNSET:
            field_dict["type"] = type_
        if url is not UNSET:
            field_dict["url"] = url
        if base64 is not UNSET:
            field_dict["base64"] = base64
        if filename is not UNSET:
            field_dict["filename"] = filename
        if mime_type is not UNSET:
            field_dict["mime_type"] = mime_type

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        type_ = d.pop("type", UNSET)

        url = d.pop("url", UNSET)

        base64 = d.pop("base64", UNSET)

        filename = d.pop("filename", UNSET)

        mime_type = d.pop("mime_type", UNSET)

        chat_attachment_request = cls(
            type_=type_,
            url=url,
            base64=base64,
            filename=filename,
            mime_type=mime_type,
        )

        chat_attachment_request.additional_properties = d
        return chat_attachment_request

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
