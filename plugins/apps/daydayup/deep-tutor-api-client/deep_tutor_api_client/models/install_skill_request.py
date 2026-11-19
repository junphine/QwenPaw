from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="InstallSkillRequest")


@_attrs_define
class InstallSkillRequest:
    """Install a hub skill into the caller's own skill layer.

    ``ref`` is a ``<hub>:<slug>[@version]`` reference (the bare hub prefix
    defaults to ``eduhub``). The web "import from EduHub" flow always builds an
    ``eduhub:`` ref so a spoofed bridge message can't redirect the install to an
    arbitrary registry.

        Attributes:
            ref (str):
            name (None | str | Unset):
            force (bool | Unset):  Default: False.
            allow_unverified (bool | Unset):  Default: False.
    """

    ref: str
    name: None | str | Unset = UNSET
    force: bool | Unset = False
    allow_unverified: bool | Unset = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ref = self.ref

        name: None | str | Unset
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name

        force = self.force

        allow_unverified = self.allow_unverified

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ref": ref,
            }
        )
        if name is not UNSET:
            field_dict["name"] = name
        if force is not UNSET:
            field_dict["force"] = force
        if allow_unverified is not UNSET:
            field_dict["allow_unverified"] = allow_unverified

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        ref = d.pop("ref")

        def _parse_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        name = _parse_name(d.pop("name", UNSET))

        force = d.pop("force", UNSET)

        allow_unverified = d.pop("allow_unverified", UNSET)

        install_skill_request = cls(
            ref=ref,
            name=name,
            force=force,
            allow_unverified=allow_unverified,
        )

        install_skill_request.additional_properties = d
        return install_skill_request

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
