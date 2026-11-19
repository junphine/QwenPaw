from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="DeviceCredentialCreateRequest")


@_attrs_define
class DeviceCredentialCreateRequest:
    """Admin payload for issuing a local ordinary-user device credential.

    Attributes:
        user_id (str):
        device_name (str):
        expires_in_days (int):
        daily_limit_minutes (int):
    """

    user_id: str
    device_name: str
    expires_in_days: int
    daily_limit_minutes: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        user_id = self.user_id

        device_name = self.device_name

        expires_in_days = self.expires_in_days

        daily_limit_minutes = self.daily_limit_minutes

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "user_id": user_id,
                "device_name": device_name,
                "expires_in_days": expires_in_days,
                "daily_limit_minutes": daily_limit_minutes,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        user_id = d.pop("user_id")

        device_name = d.pop("device_name")

        expires_in_days = d.pop("expires_in_days")

        daily_limit_minutes = d.pop("daily_limit_minutes")

        device_credential_create_request = cls(
            user_id=user_id,
            device_name=device_name,
            expires_in_days=expires_in_days,
            daily_limit_minutes=daily_limit_minutes,
        )

        device_credential_create_request.additional_properties = d
        return device_credential_create_request

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
