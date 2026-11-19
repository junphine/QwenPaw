from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ConnectKiwixRequest")


@_attrs_define
class ConnectKiwixRequest:
    """
    Attributes:
        server_url (str):
        zim_name (str):
        name (str):
    """

    server_url: str
    zim_name: str
    name: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        server_url = self.server_url

        zim_name = self.zim_name

        name = self.name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "server_url": server_url,
                "zim_name": zim_name,
                "name": name,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        server_url = d.pop("server_url")

        zim_name = d.pop("zim_name")

        name = d.pop("name")

        connect_kiwix_request = cls(
            server_url=server_url,
            zim_name=zim_name,
            name=name,
        )

        connect_kiwix_request.additional_properties = d
        return connect_kiwix_request

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
