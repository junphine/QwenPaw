from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.servers import Servers


T = TypeVar("T", bound="MCPSettingsPayload")


@_attrs_define
class MCPSettingsPayload:
    """
    Attributes:
        servers (Servers | Unset):
    """

    servers: Servers | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        servers: dict[str, Any] | Unset = UNSET
        if not isinstance(self.servers, Unset):
            servers = self.servers.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if servers is not UNSET:
            field_dict["servers"] = servers

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.servers import Servers  # noqa: PLC0415

        d = dict(src_dict)
        _servers = d.pop("servers", UNSET)
        servers: Servers | Unset
        if isinstance(_servers, Unset):
            servers = UNSET
        else:
            servers = Servers.from_dict(_servers)

        mcp_settings_payload = cls(
            servers=servers,
        )

        mcp_settings_payload.additional_properties = d
        return mcp_settings_payload

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
