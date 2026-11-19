from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="NetworkSettingsUpdate")


@_attrs_define
class NetworkSettingsUpdate:
    """
    Attributes:
        backend_port (int):
        frontend_port (int):
        public_api_base (str | Unset):  Default: ''.
        cors_origins (list[str] | Unset):
    """

    backend_port: int
    frontend_port: int
    public_api_base: str | Unset = ""
    cors_origins: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        backend_port = self.backend_port

        frontend_port = self.frontend_port

        public_api_base = self.public_api_base

        cors_origins: list[str] | Unset = UNSET
        if not isinstance(self.cors_origins, Unset):
            cors_origins = self.cors_origins

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "backend_port": backend_port,
                "frontend_port": frontend_port,
            }
        )
        if public_api_base is not UNSET:
            field_dict["public_api_base"] = public_api_base
        if cors_origins is not UNSET:
            field_dict["cors_origins"] = cors_origins

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        backend_port = d.pop("backend_port")

        frontend_port = d.pop("frontend_port")

        public_api_base = d.pop("public_api_base", UNSET)

        cors_origins = cast(list[str], d.pop("cors_origins", UNSET))

        network_settings_update = cls(
            backend_port=backend_port,
            frontend_port=frontend_port,
            public_api_base=public_api_base,
            cors_origins=cors_origins,
        )

        network_settings_update.additional_properties = d
        return network_settings_update

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
