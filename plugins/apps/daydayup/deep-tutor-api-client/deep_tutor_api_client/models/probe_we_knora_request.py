from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ProbeWeKnoraRequest")


@_attrs_define
class ProbeWeKnoraRequest:
    """
    Attributes:
        server_url (str):
        api_key (str):
        knowledge_base_id (str):
    """

    server_url: str
    api_key: str
    knowledge_base_id: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        server_url = self.server_url

        api_key = self.api_key

        knowledge_base_id = self.knowledge_base_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "server_url": server_url,
                "api_key": api_key,
                "knowledge_base_id": knowledge_base_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        server_url = d.pop("server_url")

        api_key = d.pop("api_key")

        knowledge_base_id = d.pop("knowledge_base_id")

        probe_we_knora_request = cls(
            server_url=server_url,
            api_key=api_key,
            knowledge_base_id=knowledge_base_id,
        )

        probe_we_knora_request.additional_properties = d
        return probe_we_knora_request

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
