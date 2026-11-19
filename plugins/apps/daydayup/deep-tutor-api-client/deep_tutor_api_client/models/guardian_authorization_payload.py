from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GuardianAuthorizationPayload")


@_attrs_define
class GuardianAuthorizationPayload:
    """
    Attributes:
        guardian_user_id (str):
        learner_user_id (str):
        permissions (list[str] | Unset):
    """

    guardian_user_id: str
    learner_user_id: str
    permissions: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        guardian_user_id = self.guardian_user_id

        learner_user_id = self.learner_user_id

        permissions: list[str] | Unset = UNSET
        if not isinstance(self.permissions, Unset):
            permissions = self.permissions

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "guardian_user_id": guardian_user_id,
                "learner_user_id": learner_user_id,
            }
        )
        if permissions is not UNSET:
            field_dict["permissions"] = permissions

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        guardian_user_id = d.pop("guardian_user_id")

        learner_user_id = d.pop("learner_user_id")

        permissions = cast(list[str], d.pop("permissions", UNSET))

        guardian_authorization_payload = cls(
            guardian_user_id=guardian_user_id,
            learner_user_id=learner_user_id,
            permissions=permissions,
        )

        guardian_authorization_payload.additional_properties = d
        return guardian_authorization_payload

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
