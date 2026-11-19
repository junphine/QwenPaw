from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.extensions import Extensions
    from ..models.settings_draft_payload_catalog_type_0 import SettingsDraftPayloadCatalogType0


T = TypeVar("T", bound="SettingsDraftPayload")


@_attrs_define
class SettingsDraftPayload:
    """The unapplied settings envelope, as the settings UI holds it.

    Attributes:
        catalog (None | SettingsDraftPayloadCatalogType0 | Unset):
        extensions (Extensions | Unset):
    """

    catalog: None | SettingsDraftPayloadCatalogType0 | Unset = UNSET
    extensions: Extensions | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.settings_draft_payload_catalog_type_0 import SettingsDraftPayloadCatalogType0  # noqa: PLC0415

        catalog: dict[str, Any] | None | Unset
        if isinstance(self.catalog, Unset):
            catalog = UNSET
        elif isinstance(self.catalog, SettingsDraftPayloadCatalogType0):
            catalog = self.catalog.to_dict()
        else:
            catalog = self.catalog

        extensions: dict[str, Any] | Unset = UNSET
        if not isinstance(self.extensions, Unset):
            extensions = self.extensions.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if catalog is not UNSET:
            field_dict["catalog"] = catalog
        if extensions is not UNSET:
            field_dict["extensions"] = extensions

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.extensions import Extensions  # noqa: PLC0415
        from ..models.settings_draft_payload_catalog_type_0 import SettingsDraftPayloadCatalogType0  # noqa: PLC0415

        d = dict(src_dict)

        def _parse_catalog(data: object) -> None | SettingsDraftPayloadCatalogType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                catalog_type_0 = SettingsDraftPayloadCatalogType0.from_dict(data)

                return catalog_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | SettingsDraftPayloadCatalogType0 | Unset, data)

        catalog = _parse_catalog(d.pop("catalog", UNSET))

        _extensions = d.pop("extensions", UNSET)
        extensions: Extensions | Unset
        if isinstance(_extensions, Unset):
            extensions = UNSET
        else:
            extensions = Extensions.from_dict(_extensions)

        settings_draft_payload = cls(
            catalog=catalog,
            extensions=extensions,
        )

        settings_draft_payload.additional_properties = d
        return settings_draft_payload

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
