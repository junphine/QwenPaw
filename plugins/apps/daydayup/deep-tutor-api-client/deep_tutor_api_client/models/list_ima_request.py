from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ListImaRequest")


@_attrs_define
class ListImaRequest:
    """
    Attributes:
        client_id (str | Unset):  Default: ''.
        api_key (str | Unset):  Default: ''.
        cursor (str | Unset):  Default: ''.
        limit (int | Unset):  Default: 20.
    """

    client_id: str | Unset = ""
    api_key: str | Unset = ""
    cursor: str | Unset = ""
    limit: int | Unset = 20
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        client_id = self.client_id

        api_key = self.api_key

        cursor = self.cursor

        limit = self.limit

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if client_id is not UNSET:
            field_dict["client_id"] = client_id
        if api_key is not UNSET:
            field_dict["api_key"] = api_key
        if cursor is not UNSET:
            field_dict["cursor"] = cursor
        if limit is not UNSET:
            field_dict["limit"] = limit

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        client_id = d.pop("client_id", UNSET)

        api_key = d.pop("api_key", UNSET)

        cursor = d.pop("cursor", UNSET)

        limit = d.pop("limit", UNSET)

        list_ima_request = cls(
            client_id=client_id,
            api_key=api_key,
            cursor=cursor,
            limit=limit,
        )

        list_ima_request.additional_properties = d
        return list_ima_request

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
