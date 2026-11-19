from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.tool_alias_payload import ToolAliasPayload


T = TypeVar("T", bound="ToolHintsPayload")


@_attrs_define
class ToolHintsPayload:
    """
    Attributes:
        short_description (str | Unset):  Default: ''.
        when_to_use (str | Unset):  Default: ''.
        input_format (str | Unset):  Default: ''.
        guideline (str | Unset):  Default: ''.
        note (str | Unset):  Default: ''.
        phase (str | Unset):  Default: ''.
        aliases (list[ToolAliasPayload] | Unset):
    """

    short_description: str | Unset = ""
    when_to_use: str | Unset = ""
    input_format: str | Unset = ""
    guideline: str | Unset = ""
    note: str | Unset = ""
    phase: str | Unset = ""
    aliases: list[ToolAliasPayload] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        short_description = self.short_description

        when_to_use = self.when_to_use

        input_format = self.input_format

        guideline = self.guideline

        note = self.note

        phase = self.phase

        aliases: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.aliases, Unset):
            aliases = []
            for aliases_item_data in self.aliases:
                aliases_item = aliases_item_data.to_dict()
                aliases.append(aliases_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if short_description is not UNSET:
            field_dict["short_description"] = short_description
        if when_to_use is not UNSET:
            field_dict["when_to_use"] = when_to_use
        if input_format is not UNSET:
            field_dict["input_format"] = input_format
        if guideline is not UNSET:
            field_dict["guideline"] = guideline
        if note is not UNSET:
            field_dict["note"] = note
        if phase is not UNSET:
            field_dict["phase"] = phase
        if aliases is not UNSET:
            field_dict["aliases"] = aliases

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.tool_alias_payload import ToolAliasPayload  # noqa: PLC0415

        d = dict(src_dict)
        short_description = d.pop("short_description", UNSET)

        when_to_use = d.pop("when_to_use", UNSET)

        input_format = d.pop("input_format", UNSET)

        guideline = d.pop("guideline", UNSET)

        note = d.pop("note", UNSET)

        phase = d.pop("phase", UNSET)

        _aliases = d.pop("aliases", UNSET)
        aliases: list[ToolAliasPayload] | Unset = UNSET
        if _aliases is not UNSET:
            aliases = []
            for aliases_item_data in _aliases:
                aliases_item = ToolAliasPayload.from_dict(aliases_item_data)

                aliases.append(aliases_item)

        tool_hints_payload = cls(
            short_description=short_description,
            when_to_use=when_to_use,
            input_format=input_format,
            guideline=guideline,
            note=note,
            phase=phase,
            aliases=aliases,
        )

        tool_hints_payload.additional_properties = d
        return tool_hints_payload

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
