from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="InvidiousSettings")


@_attrs_define
class InvidiousSettings:
    """
    Attributes:
        api_base_url (str | Unset):  Default: ''.
        public_base_url (str | Unset):  Default: ''.
    """

    api_base_url: str | Unset = ""
    public_base_url: str | Unset = ""
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        api_base_url = self.api_base_url

        public_base_url = self.public_base_url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if api_base_url is not UNSET:
            field_dict["api_base_url"] = api_base_url
        if public_base_url is not UNSET:
            field_dict["public_base_url"] = public_base_url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        api_base_url = d.pop("api_base_url", UNSET)

        public_base_url = d.pop("public_base_url", UNSET)

        invidious_settings = cls(
            api_base_url=api_base_url,
            public_base_url=public_base_url,
        )

        invidious_settings.additional_properties = d
        return invidious_settings

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
