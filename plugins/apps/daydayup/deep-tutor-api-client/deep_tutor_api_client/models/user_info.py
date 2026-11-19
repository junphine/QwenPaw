from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.user_info_preset import UserInfoPreset, check_user_info_preset
from ..types import UNSET, Unset

T = TypeVar("T", bound="UserInfo")


@_attrs_define
class UserInfo:
    """Single user record returned by the GET /users and /profile endpoints.

    Attributes:
        username (str):
        role (str):
        created_at (str):
        id (str | Unset):  Default: ''.
        disabled (bool | Unset):  Default: False.
        avatar (str | Unset):  Default: ''.
        preset (UserInfoPreset | Unset):  Default: 'standard'.
        must_change_password (bool | Unset):  Default: False.
        can_change_password (bool | Unset):  Default: False.
    """

    username: str
    role: str
    created_at: str
    id: str | Unset = ""
    disabled: bool | Unset = False
    avatar: str | Unset = ""
    preset: UserInfoPreset | Unset = "standard"
    must_change_password: bool | Unset = False
    can_change_password: bool | Unset = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        username = self.username

        role = self.role

        created_at = self.created_at

        id = self.id

        disabled = self.disabled

        avatar = self.avatar

        preset: str | Unset = UNSET
        if not isinstance(self.preset, Unset):
            preset = self.preset

        must_change_password = self.must_change_password

        can_change_password = self.can_change_password

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "username": username,
                "role": role,
                "created_at": created_at,
            }
        )
        if id is not UNSET:
            field_dict["id"] = id
        if disabled is not UNSET:
            field_dict["disabled"] = disabled
        if avatar is not UNSET:
            field_dict["avatar"] = avatar
        if preset is not UNSET:
            field_dict["preset"] = preset
        if must_change_password is not UNSET:
            field_dict["must_change_password"] = must_change_password
        if can_change_password is not UNSET:
            field_dict["can_change_password"] = can_change_password

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        username = d.pop("username")

        role = d.pop("role")

        created_at = d.pop("created_at")

        id = d.pop("id", UNSET)

        disabled = d.pop("disabled", UNSET)

        avatar = d.pop("avatar", UNSET)

        _preset = d.pop("preset", UNSET)
        preset: UserInfoPreset | Unset
        if isinstance(_preset, Unset):
            preset = UNSET
        else:
            preset = check_user_info_preset(_preset)

        must_change_password = d.pop("must_change_password", UNSET)

        can_change_password = d.pop("can_change_password", UNSET)

        user_info = cls(
            username=username,
            role=role,
            created_at=created_at,
            id=id,
            disabled=disabled,
            avatar=avatar,
            preset=preset,
            must_change_password=must_change_password,
            can_change_password=can_change_password,
        )

        user_info.additional_properties = d
        return user_info

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
