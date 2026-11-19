from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="SyncResponse")


@_attrs_define
class SyncResponse:
    """
    Attributes:
        stored (int):
        updated (int):
        deleted (int):
        new_cursor (str):
    """

    stored: int
    updated: int
    deleted: int
    new_cursor: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        stored = self.stored

        updated = self.updated

        deleted = self.deleted

        new_cursor = self.new_cursor

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "stored": stored,
                "updated": updated,
                "deleted": deleted,
                "new_cursor": new_cursor,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        stored = d.pop("stored")

        updated = d.pop("updated")

        deleted = d.pop("deleted")

        new_cursor = d.pop("new_cursor")

        sync_response = cls(
            stored=stored,
            updated=updated,
            deleted=deleted,
            new_cursor=new_cursor,
        )

        sync_response.additional_properties = d
        return sync_response

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
