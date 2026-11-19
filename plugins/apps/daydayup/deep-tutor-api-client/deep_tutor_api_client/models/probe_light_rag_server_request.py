from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ProbeLightRagServerRequest")


@_attrs_define
class ProbeLightRagServerRequest:
    """
    Attributes:
        server_url (str):
        api_key (str | Unset):  Default: ''.
        use_saved_api_key (bool | Unset):  Default: False.
    """

    server_url: str
    api_key: str | Unset = ""
    use_saved_api_key: bool | Unset = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        server_url = self.server_url

        api_key = self.api_key

        use_saved_api_key = self.use_saved_api_key

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "server_url": server_url,
            }
        )
        if api_key is not UNSET:
            field_dict["api_key"] = api_key
        if use_saved_api_key is not UNSET:
            field_dict["use_saved_api_key"] = use_saved_api_key

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        server_url = d.pop("server_url")

        api_key = d.pop("api_key", UNSET)

        use_saved_api_key = d.pop("use_saved_api_key", UNSET)

        probe_light_rag_server_request = cls(
            server_url=server_url,
            api_key=api_key,
            use_saved_api_key=use_saved_api_key,
        )

        probe_light_rag_server_request.additional_properties = d
        return probe_light_rag_server_request

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
