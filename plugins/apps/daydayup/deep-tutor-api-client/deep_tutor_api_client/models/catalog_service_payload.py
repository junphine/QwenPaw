from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.catalog_service_payload_service import CatalogServicePayloadService, check_catalog_service_payload_service

if TYPE_CHECKING:
    from ..models.config import Config


T = TypeVar("T", bound="CatalogServicePayload")


@_attrs_define
class CatalogServicePayload:
    """One model-catalog service to promote without touching other drafts.

    Attributes:
        service (CatalogServicePayloadService):
        config (Config):
    """

    service: CatalogServicePayloadService
    config: Config
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        service: str = self.service

        config = self.config.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "service": service,
                "config": config,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.config import Config  # noqa: PLC0415

        d = dict(src_dict)
        service = check_catalog_service_payload_service(d.pop("service"))

        config = Config.from_dict(d.pop("config"))

        catalog_service_payload = cls(
            service=service,
            config=config,
        )

        catalog_service_payload.additional_properties = d
        return catalog_service_payload

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
