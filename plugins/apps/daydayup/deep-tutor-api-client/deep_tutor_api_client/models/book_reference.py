from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="BookReference")


@_attrs_define
class BookReference:
    """
    Attributes:
        book_id (str):
        page_ids (list[str] | Unset):
    """

    book_id: str
    page_ids: list[str] | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        book_id = self.book_id

        page_ids: list[str] | Unset = UNSET
        if not isinstance(self.page_ids, Unset):
            page_ids = self.page_ids

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "book_id": book_id,
            }
        )
        if page_ids is not UNSET:
            field_dict["page_ids"] = page_ids

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        book_id = d.pop("book_id")

        page_ids = cast(list[str], d.pop("page_ids", UNSET))

        book_reference = cls(
            book_id=book_id,
            page_ids=page_ids,
        )

        return book_reference
