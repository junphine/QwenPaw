from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="LinkedFolderInfo")


@_attrs_define
class LinkedFolderInfo:
    """Response model for linked folder information.

    Attributes:
        id (str):
        path (str):
        added_at (str):
        file_count (int):
        last_sync (None | str | Unset):
    """

    id: str
    path: str
    added_at: str
    file_count: int
    last_sync: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        path = self.path

        added_at = self.added_at

        file_count = self.file_count

        last_sync: None | str | Unset
        if isinstance(self.last_sync, Unset):
            last_sync = UNSET
        else:
            last_sync = self.last_sync

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "path": path,
                "added_at": added_at,
                "file_count": file_count,
            }
        )
        if last_sync is not UNSET:
            field_dict["last_sync"] = last_sync

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        path = d.pop("path")

        added_at = d.pop("added_at")

        file_count = d.pop("file_count")

        def _parse_last_sync(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        last_sync = _parse_last_sync(d.pop("last_sync", UNSET))

        linked_folder_info = cls(
            id=id,
            path=path,
            added_at=added_at,
            file_count=file_count,
            last_sync=last_sync,
        )

        linked_folder_info.additional_properties = d
        return linked_folder_info

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
