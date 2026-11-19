from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="AnswerImageItem")


@_attrs_define
class AnswerImageItem:
    """Persisted reference to one image attached to a learner's answer.

    The bytes live in the AttachmentStore at ``url``; we never round-trip
    base64 back to the client so notebook lookups stay cheap.

        Attributes:
            id (str | Unset):  Default: ''.
            url (str | Unset):  Default: ''.
            filename (str | Unset):  Default: ''.
            mime_type (str | Unset):  Default: ''.
    """

    id: str | Unset = ""
    url: str | Unset = ""
    filename: str | Unset = ""
    mime_type: str | Unset = ""
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        url = self.url

        filename = self.filename

        mime_type = self.mime_type

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if url is not UNSET:
            field_dict["url"] = url
        if filename is not UNSET:
            field_dict["filename"] = filename
        if mime_type is not UNSET:
            field_dict["mime_type"] = mime_type

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        url = d.pop("url", UNSET)

        filename = d.pop("filename", UNSET)

        mime_type = d.pop("mime_type", UNSET)

        answer_image_item = cls(
            id=id,
            url=url,
            filename=filename,
            mime_type=mime_type,
        )

        answer_image_item.additional_properties = d
        return answer_image_item

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
