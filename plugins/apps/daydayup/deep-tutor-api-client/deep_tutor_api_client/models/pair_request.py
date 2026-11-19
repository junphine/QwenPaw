from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PairRequest")


@_attrs_define
class PairRequest:
    """
    Attributes:
        device_name (str | Unset):  Default: ''.
        device_kind (str | Unset):  Default: 'macos'.
    """

    device_name: str | Unset = ""
    device_kind: str | Unset = "macos"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        device_name = self.device_name

        device_kind = self.device_kind

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if device_name is not UNSET:
            field_dict["device_name"] = device_name
        if device_kind is not UNSET:
            field_dict["device_kind"] = device_kind

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        device_name = d.pop("device_name", UNSET)

        device_kind = d.pop("device_kind", UNSET)

        pair_request = cls(
            device_name=device_name,
            device_kind=device_kind,
        )

        pair_request.additional_properties = d
        return pair_request

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
