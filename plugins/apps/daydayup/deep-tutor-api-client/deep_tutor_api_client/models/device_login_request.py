from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="DeviceLoginRequest")


@_attrs_define
class DeviceLoginRequest:
    """Payload for the built-in device-credential login endpoint.

    Attributes:
        pairing_code (str):
        pin (str):
    """

    pairing_code: str
    pin: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        pairing_code = self.pairing_code

        pin = self.pin

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "pairing_code": pairing_code,
                "pin": pin,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        pairing_code = d.pop("pairing_code")

        pin = d.pop("pin")

        device_login_request = cls(
            pairing_code=pairing_code,
            pin=pin,
        )

        device_login_request.additional_properties = d
        return device_login_request

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
