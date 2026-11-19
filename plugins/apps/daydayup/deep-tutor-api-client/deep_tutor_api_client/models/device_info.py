from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="DeviceInfo")


@_attrs_define
class DeviceInfo:
    """
    Attributes:
        device_id (str):
        device_name (str):
        device_kind (str):
        paired_at (str):
        last_seen (str):
        active (bool):
    """

    device_id: str
    device_name: str
    device_kind: str
    paired_at: str
    last_seen: str
    active: bool
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        device_id = self.device_id

        device_name = self.device_name

        device_kind = self.device_kind

        paired_at = self.paired_at

        last_seen = self.last_seen

        active = self.active

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "device_id": device_id,
                "device_name": device_name,
                "device_kind": device_kind,
                "paired_at": paired_at,
                "last_seen": last_seen,
                "active": active,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        device_id = d.pop("device_id")

        device_name = d.pop("device_name")

        device_kind = d.pop("device_kind")

        paired_at = d.pop("paired_at")

        last_seen = d.pop("last_seen")

        active = d.pop("active")

        device_info = cls(
            device_id=device_id,
            device_name=device_name,
            device_kind=device_kind,
            paired_at=paired_at,
            last_seen=last_seen,
            active=active,
        )

        device_info.additional_properties = d
        return device_info

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
