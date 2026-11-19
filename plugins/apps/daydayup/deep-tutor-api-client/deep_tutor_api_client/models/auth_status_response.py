from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.auth_status_response_preset_type_0 import (
    AuthStatusResponsePresetType0,
    check_auth_status_response_preset_type_0,
)
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.auth_status_response_learning_policy_type_0 import AuthStatusResponseLearningPolicyType0


T = TypeVar("T", bound="AuthStatusResponse")


@_attrs_define
class AuthStatusResponse:
    """Response body for the GET /status endpoint.

    Attributes:
        enabled (bool):
        authenticated (bool):
        user_id (None | str | Unset):
        username (None | str | Unset):
        role (None | str | Unset):
        is_admin (bool | Unset):  Default: False.
        avatar (str | Unset):  Default: ''.
        preset (AuthStatusResponsePresetType0 | None | Unset):
        learning_policy (AuthStatusResponseLearningPolicyType0 | None | Unset):
    """

    enabled: bool
    authenticated: bool
    user_id: None | str | Unset = UNSET
    username: None | str | Unset = UNSET
    role: None | str | Unset = UNSET
    is_admin: bool | Unset = False
    avatar: str | Unset = ""
    preset: AuthStatusResponsePresetType0 | None | Unset = UNSET
    learning_policy: AuthStatusResponseLearningPolicyType0 | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.auth_status_response_learning_policy_type_0 import (
            AuthStatusResponseLearningPolicyType0,  # noqa: PLC0415
        )

        enabled = self.enabled

        authenticated = self.authenticated

        user_id: None | str | Unset
        if isinstance(self.user_id, Unset):
            user_id = UNSET
        else:
            user_id = self.user_id

        username: None | str | Unset
        if isinstance(self.username, Unset):
            username = UNSET
        else:
            username = self.username

        role: None | str | Unset
        if isinstance(self.role, Unset):
            role = UNSET
        else:
            role = self.role

        is_admin = self.is_admin

        avatar = self.avatar

        preset: None | str | Unset
        if isinstance(self.preset, Unset):
            preset = UNSET
        elif isinstance(self.preset, str):
            preset = self.preset
        else:
            preset = self.preset

        learning_policy: dict[str, Any] | None | Unset
        if isinstance(self.learning_policy, Unset):
            learning_policy = UNSET
        elif isinstance(self.learning_policy, AuthStatusResponseLearningPolicyType0):
            learning_policy = self.learning_policy.to_dict()
        else:
            learning_policy = self.learning_policy

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "enabled": enabled,
                "authenticated": authenticated,
            }
        )
        if user_id is not UNSET:
            field_dict["user_id"] = user_id
        if username is not UNSET:
            field_dict["username"] = username
        if role is not UNSET:
            field_dict["role"] = role
        if is_admin is not UNSET:
            field_dict["is_admin"] = is_admin
        if avatar is not UNSET:
            field_dict["avatar"] = avatar
        if preset is not UNSET:
            field_dict["preset"] = preset
        if learning_policy is not UNSET:
            field_dict["learning_policy"] = learning_policy

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.auth_status_response_learning_policy_type_0 import (
            AuthStatusResponseLearningPolicyType0,  # noqa: PLC0415
        )

        d = dict(src_dict)
        enabled = d.pop("enabled")

        authenticated = d.pop("authenticated")

        def _parse_user_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        user_id = _parse_user_id(d.pop("user_id", UNSET))

        def _parse_username(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        username = _parse_username(d.pop("username", UNSET))

        def _parse_role(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        role = _parse_role(d.pop("role", UNSET))

        is_admin = d.pop("is_admin", UNSET)

        avatar = d.pop("avatar", UNSET)

        def _parse_preset(data: object) -> AuthStatusResponsePresetType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                preset_type_0 = check_auth_status_response_preset_type_0(data)

                return preset_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(AuthStatusResponsePresetType0 | None | Unset, data)

        preset = _parse_preset(d.pop("preset", UNSET))

        def _parse_learning_policy(data: object) -> AuthStatusResponseLearningPolicyType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                learning_policy_type_0 = AuthStatusResponseLearningPolicyType0.from_dict(data)

                return learning_policy_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(AuthStatusResponseLearningPolicyType0 | None | Unset, data)

        learning_policy = _parse_learning_policy(d.pop("learning_policy", UNSET))

        auth_status_response = cls(
            enabled=enabled,
            authenticated=authenticated,
            user_id=user_id,
            username=username,
            role=role,
            is_admin=is_admin,
            avatar=avatar,
            preset=preset,
            learning_policy=learning_policy,
        )

        auth_status_response.additional_properties = d
        return auth_status_response

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
