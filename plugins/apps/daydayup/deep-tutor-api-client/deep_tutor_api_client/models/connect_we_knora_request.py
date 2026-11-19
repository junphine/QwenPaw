from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ConnectWeKnoraRequest")


@_attrs_define
class ConnectWeKnoraRequest:
    """
    Attributes:
        name (str):
        server_url (str):
        api_key (str):
        knowledge_base_id (str):
        description (str | Unset):  Default: ''.
    """

    name: str
    server_url: str
    api_key: str
    knowledge_base_id: str
    description: str | Unset = ""
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        server_url = self.server_url

        api_key = self.api_key

        knowledge_base_id = self.knowledge_base_id

        description = self.description

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "server_url": server_url,
                "api_key": api_key,
                "knowledge_base_id": knowledge_base_id,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        server_url = d.pop("server_url")

        api_key = d.pop("api_key")

        knowledge_base_id = d.pop("knowledge_base_id")

        description = d.pop("description", UNSET)

        connect_we_knora_request = cls(
            name=name,
            server_url=server_url,
            api_key=api_key,
            knowledge_base_id=knowledge_base_id,
            description=description,
        )

        connect_we_knora_request.additional_properties = d
        return connect_we_knora_request

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
