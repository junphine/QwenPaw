from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="AnswerImageUpload")


@_attrs_define
class AnswerImageUpload:
    """One image attached to the learner's answer.

    Either ``base64`` (new upload) or ``url`` (re-submit of an already
    persisted image) must be set. ``id`` is preserved when the client
    sends one so the same logical image keeps a stable AttachmentStore
    record across resubmissions.

        Attributes:
            id (str | Unset):  Default: ''.
            base64 (str | Unset):  Default: ''.
            url (str | Unset):  Default: ''.
            filename (str | Unset):  Default: 'answer.png'.
            mime_type (str | Unset):  Default: 'image/png'.
    """

    id: str | Unset = ""
    base64: str | Unset = ""
    url: str | Unset = ""
    filename: str | Unset = "answer.png"
    mime_type: str | Unset = "image/png"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        base64 = self.base64

        url = self.url

        filename = self.filename

        mime_type = self.mime_type

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if base64 is not UNSET:
            field_dict["base64"] = base64
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

        base64 = d.pop("base64", UNSET)

        url = d.pop("url", UNSET)

        filename = d.pop("filename", UNSET)

        mime_type = d.pop("mime_type", UNSET)

        answer_image_upload = cls(
            id=id,
            base64=base64,
            url=url,
            filename=filename,
            mime_type=mime_type,
        )

        answer_image_upload.additional_properties = d
        return answer_image_upload

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
