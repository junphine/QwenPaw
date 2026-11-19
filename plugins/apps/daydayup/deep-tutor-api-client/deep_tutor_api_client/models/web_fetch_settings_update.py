from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="WebFetchSettingsUpdate")


@_attrs_define
class WebFetchSettingsUpdate:
    """Web fetch backend selection — the ``web_fetch.backend`` settings row.

    The value names an entry in the backend's ``FETCH_PROVIDERS`` spec table;
    the endpoint validates against it because the choice set is owned by the
    backend, not by this schema.

        Attributes:
            backend (str):
    """

    backend: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        backend = self.backend

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "backend": backend,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        backend = d.pop("backend")

        web_fetch_settings_update = cls(
            backend=backend,
        )

        web_fetch_settings_update.additional_properties = d
        return web_fetch_settings_update

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
