from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.sync_object_in import SyncObjectIn


T = TypeVar("T", bound="SyncRequest")


@_attrs_define
class SyncRequest:
    """
    Attributes:
        cursor (str | Unset):  Default: ''.
        objects (list[SyncObjectIn] | Unset):
        deleted_ids (list[str] | Unset):
    """

    cursor: str | Unset = ""
    objects: list[SyncObjectIn] | Unset = UNSET
    deleted_ids: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        cursor = self.cursor

        objects: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.objects, Unset):
            objects = []
            for objects_item_data in self.objects:
                objects_item = objects_item_data.to_dict()
                objects.append(objects_item)

        deleted_ids: list[str] | Unset = UNSET
        if not isinstance(self.deleted_ids, Unset):
            deleted_ids = self.deleted_ids

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if cursor is not UNSET:
            field_dict["cursor"] = cursor
        if objects is not UNSET:
            field_dict["objects"] = objects
        if deleted_ids is not UNSET:
            field_dict["deleted_ids"] = deleted_ids

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.sync_object_in import SyncObjectIn  # noqa: PLC0415

        d = dict(src_dict)
        cursor = d.pop("cursor", UNSET)

        _objects = d.pop("objects", UNSET)
        objects: list[SyncObjectIn] | Unset = UNSET
        if _objects is not UNSET:
            objects = []
            for objects_item_data in _objects:
                objects_item = SyncObjectIn.from_dict(objects_item_data)

                objects.append(objects_item)

        deleted_ids = cast(list[str], d.pop("deleted_ids", UNSET))

        sync_request = cls(
            cursor=cursor,
            objects=objects,
            deleted_ids=deleted_ids,
        )

        sync_request.additional_properties = d
        return sync_request

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
