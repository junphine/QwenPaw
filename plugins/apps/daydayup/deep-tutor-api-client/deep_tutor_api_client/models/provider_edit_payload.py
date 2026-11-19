from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.provider_edit_payload_service import ProviderEditPayloadService, check_provider_edit_payload_service
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.profile import Profile
    from ..models.provider_edit_payload_connection_type_0 import ProviderEditPayloadConnectionType0


T = TypeVar("T", bound="ProviderEditPayload")


@_attrs_define
class ProviderEditPayload:
    """
    Attributes:
        service (ProviderEditPayloadService):
        profile (Profile):
        connection (None | ProviderEditPayloadConnectionType0 | Unset):
        active_model_id (None | str | Unset):
        activate (bool | Unset):  Default: False.
    """

    service: ProviderEditPayloadService
    profile: Profile
    connection: None | ProviderEditPayloadConnectionType0 | Unset = UNSET
    active_model_id: None | str | Unset = UNSET
    activate: bool | Unset = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.provider_edit_payload_connection_type_0 import ProviderEditPayloadConnectionType0  # noqa: PLC0415

        service: str = self.service

        profile = self.profile.to_dict()

        connection: dict[str, Any] | None | Unset
        if isinstance(self.connection, Unset):
            connection = UNSET
        elif isinstance(self.connection, ProviderEditPayloadConnectionType0):
            connection = self.connection.to_dict()
        else:
            connection = self.connection

        active_model_id: None | str | Unset
        if isinstance(self.active_model_id, Unset):
            active_model_id = UNSET
        else:
            active_model_id = self.active_model_id

        activate = self.activate

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "service": service,
                "profile": profile,
            }
        )
        if connection is not UNSET:
            field_dict["connection"] = connection
        if active_model_id is not UNSET:
            field_dict["active_model_id"] = active_model_id
        if activate is not UNSET:
            field_dict["activate"] = activate

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.profile import Profile  # noqa: PLC0415
        from ..models.provider_edit_payload_connection_type_0 import ProviderEditPayloadConnectionType0  # noqa: PLC0415

        d = dict(src_dict)
        service = check_provider_edit_payload_service(d.pop("service"))

        profile = Profile.from_dict(d.pop("profile"))

        def _parse_connection(data: object) -> None | ProviderEditPayloadConnectionType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                connection_type_0 = ProviderEditPayloadConnectionType0.from_dict(data)

                return connection_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ProviderEditPayloadConnectionType0 | Unset, data)

        connection = _parse_connection(d.pop("connection", UNSET))

        def _parse_active_model_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        active_model_id = _parse_active_model_id(d.pop("active_model_id", UNSET))

        activate = d.pop("activate", UNSET)

        provider_edit_payload = cls(
            service=service,
            profile=profile,
            connection=connection,
            active_model_id=active_model_id,
            activate=activate,
        )

        provider_edit_payload.additional_properties = d
        return provider_edit_payload

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
