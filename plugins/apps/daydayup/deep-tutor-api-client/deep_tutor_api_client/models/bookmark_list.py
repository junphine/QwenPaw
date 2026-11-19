from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.bookmark_info import BookmarkInfo


T = TypeVar("T", bound="BookmarkList")


@_attrs_define
class BookmarkList:
    """
    Attributes:
        bookmarks (list[BookmarkInfo]):
    """

    bookmarks: list[BookmarkInfo]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        bookmarks = []
        for bookmarks_item_data in self.bookmarks:
            bookmarks_item = bookmarks_item_data.to_dict()
            bookmarks.append(bookmarks_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "bookmarks": bookmarks,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.bookmark_info import BookmarkInfo  # noqa: PLC0415

        d = dict(src_dict)
        bookmarks = []
        _bookmarks = d.pop("bookmarks")
        for bookmarks_item_data in _bookmarks:
            bookmarks_item = BookmarkInfo.from_dict(bookmarks_item_data)

            bookmarks.append(bookmarks_item)

        bookmark_list = cls(
            bookmarks=bookmarks,
        )

        bookmark_list.additional_properties = d
        return bookmark_list

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
