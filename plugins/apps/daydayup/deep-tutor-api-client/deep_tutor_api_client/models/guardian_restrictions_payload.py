from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="GuardianRestrictionsPayload")


@_attrs_define
class GuardianRestrictionsPayload:
    """
    Attributes:
        age_band (str):
        allow_upload (bool):
        allowed_surfaces (list[str]):
        extensions (list[str]):
    """

    age_band: str
    allow_upload: bool
    allowed_surfaces: list[str]
    extensions: list[str]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        age_band = self.age_band

        allow_upload = self.allow_upload

        allowed_surfaces = self.allowed_surfaces

        extensions = self.extensions

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "age_band": age_band,
                "allow_upload": allow_upload,
                "allowed_surfaces": allowed_surfaces,
                "extensions": extensions,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        age_band = d.pop("age_band")

        allow_upload = d.pop("allow_upload")

        allowed_surfaces = cast(list[str], d.pop("allowed_surfaces"))

        extensions = cast(list[str], d.pop("extensions"))

        guardian_restrictions_payload = cls(
            age_band=age_band,
            allow_upload=allow_upload,
            allowed_surfaces=allowed_surfaces,
            extensions=extensions,
        )

        guardian_restrictions_payload.additional_properties = d
        return guardian_restrictions_payload

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
