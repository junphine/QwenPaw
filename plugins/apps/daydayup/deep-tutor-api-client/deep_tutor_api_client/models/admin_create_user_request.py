from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.admin_create_user_request_preset import (
    AdminCreateUserRequestPreset,
    check_admin_create_user_request_preset,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="AdminCreateUserRequest")


@_attrs_define
class AdminCreateUserRequest:
    """Admin user-creation payload.

    A preset configures an ordinary account; it never becomes a third role.

        Attributes:
            username (str):
            password (str):
            preset (AdminCreateUserRequestPreset | Unset):  Default: 'standard'.
    """

    username: str
    password: str
    preset: AdminCreateUserRequestPreset | Unset = "standard"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        username = self.username

        password = self.password

        preset: str | Unset = UNSET
        if not isinstance(self.preset, Unset):
            preset = self.preset

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "username": username,
                "password": password,
            }
        )
        if preset is not UNSET:
            field_dict["preset"] = preset

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        username = d.pop("username")

        password = d.pop("password")

        _preset = d.pop("preset", UNSET)
        preset: AdminCreateUserRequestPreset | Unset
        if isinstance(_preset, Unset):
            preset = UNSET
        else:
            preset = check_admin_create_user_request_preset(_preset)

        admin_create_user_request = cls(
            username=username,
            password=password,
            preset=preset,
        )

        admin_create_user_request.additional_properties = d
        return admin_create_user_request

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
