from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="LearningCaptureCreateRequest")


@_attrs_define
class LearningCaptureCreateRequest:
    """
    Attributes:
        page_id (str):
        source_text (str):
        block_id (str | Unset):  Default: ''.
        context_before (str | Unset):  Default: ''.
        context_after (str | Unset):  Default: ''.
        source_locator (str | Unset):  Default: ''.
        book_title (str | Unset):  Default: ''.
        chapter_title (str | Unset):  Default: ''.
        user_note (str | Unset):  Default: ''.
        status (None | str | Unset):
    """

    page_id: str
    source_text: str
    block_id: str | Unset = ""
    context_before: str | Unset = ""
    context_after: str | Unset = ""
    source_locator: str | Unset = ""
    book_title: str | Unset = ""
    chapter_title: str | Unset = ""
    user_note: str | Unset = ""
    status: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        page_id = self.page_id

        source_text = self.source_text

        block_id = self.block_id

        context_before = self.context_before

        context_after = self.context_after

        source_locator = self.source_locator

        book_title = self.book_title

        chapter_title = self.chapter_title

        user_note = self.user_note

        status: None | str | Unset
        if isinstance(self.status, Unset):
            status = UNSET
        else:
            status = self.status

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "page_id": page_id,
                "source_text": source_text,
            }
        )
        if block_id is not UNSET:
            field_dict["block_id"] = block_id
        if context_before is not UNSET:
            field_dict["context_before"] = context_before
        if context_after is not UNSET:
            field_dict["context_after"] = context_after
        if source_locator is not UNSET:
            field_dict["source_locator"] = source_locator
        if book_title is not UNSET:
            field_dict["book_title"] = book_title
        if chapter_title is not UNSET:
            field_dict["chapter_title"] = chapter_title
        if user_note is not UNSET:
            field_dict["user_note"] = user_note
        if status is not UNSET:
            field_dict["status"] = status

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        page_id = d.pop("page_id")

        source_text = d.pop("source_text")

        block_id = d.pop("block_id", UNSET)

        context_before = d.pop("context_before", UNSET)

        context_after = d.pop("context_after", UNSET)

        source_locator = d.pop("source_locator", UNSET)

        book_title = d.pop("book_title", UNSET)

        chapter_title = d.pop("chapter_title", UNSET)

        user_note = d.pop("user_note", UNSET)

        def _parse_status(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        status = _parse_status(d.pop("status", UNSET))

        learning_capture_create_request = cls(
            page_id=page_id,
            source_text=source_text,
            block_id=block_id,
            context_before=context_before,
            context_after=context_after,
            source_locator=source_locator,
            book_title=book_title,
            chapter_title=chapter_title,
            user_note=user_note,
            status=status,
        )

        learning_capture_create_request.additional_properties = d
        return learning_capture_create_request

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
