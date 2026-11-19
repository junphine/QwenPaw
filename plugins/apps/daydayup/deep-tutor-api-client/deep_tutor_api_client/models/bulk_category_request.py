from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="BulkCategoryRequest")


@_attrs_define
class BulkCategoryRequest:
    """File (or unfile) many entries at once.

    One round-trip per bulk action keeps the list view consistent: the
    client re-reads once instead of racing N per-entry writes.

        Attributes:
            entry_ids (list[int]):
            category_id (int):
            link (bool | Unset):  Default: True.
    """

    entry_ids: list[int]
    category_id: int
    link: bool | Unset = True
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        entry_ids = self.entry_ids

        category_id = self.category_id

        link = self.link

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "entry_ids": entry_ids,
                "category_id": category_id,
            }
        )
        if link is not UNSET:
            field_dict["link"] = link

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        entry_ids = cast(list[int], d.pop("entry_ids"))

        category_id = d.pop("category_id")

        link = d.pop("link", UNSET)

        bulk_category_request = cls(
            entry_ids=entry_ids,
            category_id=category_id,
            link=link,
        )

        bulk_category_request.additional_properties = d
        return bulk_category_request

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
