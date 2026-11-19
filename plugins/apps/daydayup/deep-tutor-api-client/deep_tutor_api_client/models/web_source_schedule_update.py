from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="WebSourceScheduleUpdate")


@_attrs_define
class WebSourceScheduleUpdate:
    """
    Attributes:
        auto_sync_enabled (bool):
        sync_interval_hours (int | Unset):  Default: 24.
    """

    auto_sync_enabled: bool
    sync_interval_hours: int | Unset = 24
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        auto_sync_enabled = self.auto_sync_enabled

        sync_interval_hours = self.sync_interval_hours

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "auto_sync_enabled": auto_sync_enabled,
            }
        )
        if sync_interval_hours is not UNSET:
            field_dict["sync_interval_hours"] = sync_interval_hours

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        auto_sync_enabled = d.pop("auto_sync_enabled")

        sync_interval_hours = d.pop("sync_interval_hours", UNSET)

        web_source_schedule_update = cls(
            auto_sync_enabled=auto_sync_enabled,
            sync_interval_hours=sync_interval_hours,
        )

        web_source_schedule_update.additional_properties = d
        return web_source_schedule_update

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
