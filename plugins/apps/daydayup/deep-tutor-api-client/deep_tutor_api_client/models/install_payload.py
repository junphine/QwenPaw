from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.secrets import Secrets


T = TypeVar("T", bound="InstallPayload")


@_attrs_define
class InstallPayload:
    """Install a catalog entry, optionally under a different local name.

    Attributes:
        name (str | Unset):  Default: ''.
        secrets (Secrets | Unset):
    """

    name: str | Unset = ""
    secrets: Secrets | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        secrets: dict[str, Any] | Unset = UNSET
        if not isinstance(self.secrets, Unset):
            secrets = self.secrets.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if secrets is not UNSET:
            field_dict["secrets"] = secrets

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.secrets import Secrets  # noqa: PLC0415

        d = dict(src_dict)
        name = d.pop("name", UNSET)

        _secrets = d.pop("secrets", UNSET)
        secrets: Secrets | Unset
        if isinstance(_secrets, Unset):
            secrets = UNSET
        else:
            secrets = Secrets.from_dict(_secrets)

        install_payload = cls(
            name=name,
            secrets=secrets,
        )

        install_payload.additional_properties = d
        return install_payload

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
