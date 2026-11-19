from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.fetch_models_payload_service import FetchModelsPayloadService, check_fetch_models_payload_service
from ..types import UNSET, Unset

T = TypeVar("T", bound="FetchModelsPayload")


@_attrs_define
class FetchModelsPayload:
    """
    Attributes:
        binding (str | Unset):  Default: ''.
        base_url (str | Unset):  Default: ''.
        api_key (None | str | Unset):
        profile_id (None | str | Unset):
        service (FetchModelsPayloadService | Unset):  Default: 'llm'.
        api_format (None | str | Unset):
    """

    binding: str | Unset = ""
    base_url: str | Unset = ""
    api_key: None | str | Unset = UNSET
    profile_id: None | str | Unset = UNSET
    service: FetchModelsPayloadService | Unset = "llm"
    api_format: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        binding = self.binding

        base_url = self.base_url

        api_key: None | str | Unset
        if isinstance(self.api_key, Unset):
            api_key = UNSET
        else:
            api_key = self.api_key

        profile_id: None | str | Unset
        if isinstance(self.profile_id, Unset):
            profile_id = UNSET
        else:
            profile_id = self.profile_id

        service: str | Unset = UNSET
        if not isinstance(self.service, Unset):
            service = self.service

        api_format: None | str | Unset
        if isinstance(self.api_format, Unset):
            api_format = UNSET
        else:
            api_format = self.api_format

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if binding is not UNSET:
            field_dict["binding"] = binding
        if base_url is not UNSET:
            field_dict["base_url"] = base_url
        if api_key is not UNSET:
            field_dict["api_key"] = api_key
        if profile_id is not UNSET:
            field_dict["profile_id"] = profile_id
        if service is not UNSET:
            field_dict["service"] = service
        if api_format is not UNSET:
            field_dict["api_format"] = api_format

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        binding = d.pop("binding", UNSET)

        base_url = d.pop("base_url", UNSET)

        def _parse_api_key(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        api_key = _parse_api_key(d.pop("api_key", UNSET))

        def _parse_profile_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        profile_id = _parse_profile_id(d.pop("profile_id", UNSET))

        _service = d.pop("service", UNSET)
        service: FetchModelsPayloadService | Unset
        if isinstance(_service, Unset):
            service = UNSET
        else:
            service = check_fetch_models_payload_service(_service)

        def _parse_api_format(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        api_format = _parse_api_format(d.pop("api_format", UNSET))

        fetch_models_payload = cls(
            binding=binding,
            base_url=base_url,
            api_key=api_key,
            profile_id=profile_id,
            service=service,
            api_format=api_format,
        )

        fetch_models_payload.additional_properties = d
        return fetch_models_payload

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
