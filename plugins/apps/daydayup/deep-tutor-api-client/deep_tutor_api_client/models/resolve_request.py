from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ResolveRequest")


@_attrs_define
class ResolveRequest:
    """
    Attributes:
        url (str):
        language (str | Unset):  Default: ''.
        provider_override (None | str | Unset):
    """

    url: str
    language: str | Unset = ""
    provider_override: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        url = self.url

        language = self.language

        provider_override: None | str | Unset
        if isinstance(self.provider_override, Unset):
            provider_override = UNSET
        else:
            provider_override = self.provider_override

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "url": url,
            }
        )
        if language is not UNSET:
            field_dict["language"] = language
        if provider_override is not UNSET:
            field_dict["provider_override"] = provider_override

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        url = d.pop("url")

        language = d.pop("language", UNSET)

        def _parse_provider_override(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        provider_override = _parse_provider_override(d.pop("provider_override", UNSET))

        resolve_request = cls(
            url=url,
            language=language,
            provider_override=provider_override,
        )

        resolve_request.additional_properties = d
        return resolve_request

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
