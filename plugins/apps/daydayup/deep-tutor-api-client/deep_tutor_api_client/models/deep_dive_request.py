from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="DeepDiveRequest")


@_attrs_define
class DeepDiveRequest:
    """
    Attributes:
        book_id (str):
        parent_page_id (str):
        topic (str):
        block_id (None | str | Unset):
        content_type (str | Unset):  Default: 'concept'.
        expected_revision (int | None | Unset):
    """

    book_id: str
    parent_page_id: str
    topic: str
    block_id: None | str | Unset = UNSET
    content_type: str | Unset = "concept"
    expected_revision: int | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        book_id = self.book_id

        parent_page_id = self.parent_page_id

        topic = self.topic

        block_id: None | str | Unset
        if isinstance(self.block_id, Unset):
            block_id = UNSET
        else:
            block_id = self.block_id

        content_type = self.content_type

        expected_revision: int | None | Unset
        if isinstance(self.expected_revision, Unset):
            expected_revision = UNSET
        else:
            expected_revision = self.expected_revision

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "book_id": book_id,
                "parent_page_id": parent_page_id,
                "topic": topic,
            }
        )
        if block_id is not UNSET:
            field_dict["block_id"] = block_id
        if content_type is not UNSET:
            field_dict["content_type"] = content_type
        if expected_revision is not UNSET:
            field_dict["expected_revision"] = expected_revision

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        book_id = d.pop("book_id")

        parent_page_id = d.pop("parent_page_id")

        topic = d.pop("topic")

        def _parse_block_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        block_id = _parse_block_id(d.pop("block_id", UNSET))

        content_type = d.pop("content_type", UNSET)

        def _parse_expected_revision(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        expected_revision = _parse_expected_revision(d.pop("expected_revision", UNSET))

        deep_dive_request = cls(
            book_id=book_id,
            parent_page_id=parent_page_id,
            topic=topic,
            block_id=block_id,
            content_type=content_type,
            expected_revision=expected_revision,
        )

        deep_dive_request.additional_properties = d
        return deep_dive_request

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
