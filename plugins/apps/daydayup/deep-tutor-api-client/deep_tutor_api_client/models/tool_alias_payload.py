from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ToolAliasPayload")


@_attrs_define
class ToolAliasPayload:
    """
    Attributes:
        name (str):
        description (str | Unset):  Default: ''.
        input_format (str | Unset):  Default: ''.
        when_to_use (str | Unset):  Default: ''.
        phase (str | Unset):  Default: ''.
    """

    name: str
    description: str | Unset = ""
    input_format: str | Unset = ""
    when_to_use: str | Unset = ""
    phase: str | Unset = ""
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        description = self.description

        input_format = self.input_format

        when_to_use = self.when_to_use

        phase = self.phase

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if input_format is not UNSET:
            field_dict["input_format"] = input_format
        if when_to_use is not UNSET:
            field_dict["when_to_use"] = when_to_use
        if phase is not UNSET:
            field_dict["phase"] = phase

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        description = d.pop("description", UNSET)

        input_format = d.pop("input_format", UNSET)

        when_to_use = d.pop("when_to_use", UNSET)

        phase = d.pop("phase", UNSET)

        tool_alias_payload = cls(
            name=name,
            description=description,
            input_format=input_format,
            when_to_use=when_to_use,
            phase=phase,
        )

        tool_alias_payload.additional_properties = d
        return tool_alias_payload

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
