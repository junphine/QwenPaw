from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="DoclingRemoteTest")


@_attrs_define
class DoclingRemoteTest:
    """Draft Docling remote-server test. ``api_token`` is tri-state: ``None``
    falls back to the stored key, ``""`` clears it, a string supplies it (so
    the user can verify an unsaved key before saving).

        Attributes:
            api_base_url (str | Unset):  Default: 'http://localhost:5001'.
            api_token (None | str | Unset):
    """

    api_base_url: str | Unset = "http://localhost:5001"
    api_token: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        api_base_url = self.api_base_url

        api_token: None | str | Unset
        if isinstance(self.api_token, Unset):
            api_token = UNSET
        else:
            api_token = self.api_token

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if api_base_url is not UNSET:
            field_dict["api_base_url"] = api_base_url
        if api_token is not UNSET:
            field_dict["api_token"] = api_token

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        api_base_url = d.pop("api_base_url", UNSET)

        def _parse_api_token(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        api_token = _parse_api_token(d.pop("api_token", UNSET))

        docling_remote_test = cls(
            api_base_url=api_base_url,
            api_token=api_token,
        )

        docling_remote_test.additional_properties = d
        return docling_remote_test

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
