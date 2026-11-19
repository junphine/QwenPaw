from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.provider_probe_payload_service import ProviderProbePayloadService, check_provider_probe_payload_service
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.provider_probe_payload_extra_headers_type_0 import ProviderProbePayloadExtraHeadersType0


T = TypeVar("T", bound="ProviderProbePayload")


@_attrs_define
class ProviderProbePayload:
    """
    Attributes:
        binding (str | Unset):  Default: 'openai'.
        base_url (str | Unset):  Default: ''.
        api_key (list[str] | None | str | Unset):
        api_format (str | Unset):  Default: 'auto'.
        api_version (str | Unset):  Default: ''.
        extra_headers (None | ProviderProbePayloadExtraHeadersType0 | str | Unset):
        proxy (str | Unset):  Default: ''.
        service (ProviderProbePayloadService | Unset):  Default: 'llm'.
        profile_id (None | str | Unset):
        connection_id (None | str | Unset):
    """

    binding: str | Unset = "openai"
    base_url: str | Unset = ""
    api_key: list[str] | None | str | Unset = UNSET
    api_format: str | Unset = "auto"
    api_version: str | Unset = ""
    extra_headers: None | ProviderProbePayloadExtraHeadersType0 | str | Unset = UNSET
    proxy: str | Unset = ""
    service: ProviderProbePayloadService | Unset = "llm"
    profile_id: None | str | Unset = UNSET
    connection_id: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.provider_probe_payload_extra_headers_type_0 import (
            ProviderProbePayloadExtraHeadersType0,  # noqa: PLC0415
        )

        binding = self.binding

        base_url = self.base_url

        api_key: list[str] | None | str | Unset
        if isinstance(self.api_key, Unset):
            api_key = UNSET
        elif isinstance(self.api_key, list):
            api_key = self.api_key

        else:
            api_key = self.api_key

        api_format = self.api_format

        api_version = self.api_version

        extra_headers: dict[str, Any] | None | str | Unset
        if isinstance(self.extra_headers, Unset):
            extra_headers = UNSET
        elif isinstance(self.extra_headers, ProviderProbePayloadExtraHeadersType0):
            extra_headers = self.extra_headers.to_dict()
        else:
            extra_headers = self.extra_headers

        proxy = self.proxy

        service: str | Unset = UNSET
        if not isinstance(self.service, Unset):
            service = self.service

        profile_id: None | str | Unset
        if isinstance(self.profile_id, Unset):
            profile_id = UNSET
        else:
            profile_id = self.profile_id

        connection_id: None | str | Unset
        if isinstance(self.connection_id, Unset):
            connection_id = UNSET
        else:
            connection_id = self.connection_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if binding is not UNSET:
            field_dict["binding"] = binding
        if base_url is not UNSET:
            field_dict["base_url"] = base_url
        if api_key is not UNSET:
            field_dict["api_key"] = api_key
        if api_format is not UNSET:
            field_dict["api_format"] = api_format
        if api_version is not UNSET:
            field_dict["api_version"] = api_version
        if extra_headers is not UNSET:
            field_dict["extra_headers"] = extra_headers
        if proxy is not UNSET:
            field_dict["proxy"] = proxy
        if service is not UNSET:
            field_dict["service"] = service
        if profile_id is not UNSET:
            field_dict["profile_id"] = profile_id
        if connection_id is not UNSET:
            field_dict["connection_id"] = connection_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.provider_probe_payload_extra_headers_type_0 import (
            ProviderProbePayloadExtraHeadersType0,  # noqa: PLC0415
        )

        d = dict(src_dict)
        binding = d.pop("binding", UNSET)

        base_url = d.pop("base_url", UNSET)

        def _parse_api_key(data: object) -> list[str] | None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                api_key_type_1 = cast(list[str], data)

                return api_key_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | str | Unset, data)

        api_key = _parse_api_key(d.pop("api_key", UNSET))

        api_format = d.pop("api_format", UNSET)

        api_version = d.pop("api_version", UNSET)

        def _parse_extra_headers(data: object) -> None | ProviderProbePayloadExtraHeadersType0 | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                extra_headers_type_0 = ProviderProbePayloadExtraHeadersType0.from_dict(data)

                return extra_headers_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ProviderProbePayloadExtraHeadersType0 | str | Unset, data)

        extra_headers = _parse_extra_headers(d.pop("extra_headers", UNSET))

        proxy = d.pop("proxy", UNSET)

        _service = d.pop("service", UNSET)
        service: ProviderProbePayloadService | Unset
        if isinstance(_service, Unset):
            service = UNSET
        else:
            service = check_provider_probe_payload_service(_service)

        def _parse_profile_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        profile_id = _parse_profile_id(d.pop("profile_id", UNSET))

        def _parse_connection_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        connection_id = _parse_connection_id(d.pop("connection_id", UNSET))

        provider_probe_payload = cls(
            binding=binding,
            base_url=base_url,
            api_key=api_key,
            api_format=api_format,
            api_version=api_version,
            extra_headers=extra_headers,
            proxy=proxy,
            service=service,
            profile_id=profile_id,
            connection_id=connection_id,
        )

        provider_probe_payload.additional_properties = d
        return provider_probe_payload

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
