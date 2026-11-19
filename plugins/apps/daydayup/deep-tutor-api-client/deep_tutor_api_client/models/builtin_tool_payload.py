from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.description_i18n import DescriptionI18N
    from ..models.hints import Hints
    from ..models.tool_parameter_payload import ToolParameterPayload


T = TypeVar("T", bound="BuiltinToolPayload")


@_attrs_define
class BuiltinToolPayload:
    """
    Attributes:
        name (str):
        description (str):
        parameters (list[ToolParameterPayload]):
        hints (Hints):
        description_i18n (DescriptionI18N | Unset):
        aliases (list[str] | Unset):
        toggleable (bool | Unset):  Default: False.
        enabled (bool | Unset):  Default: True.
        coming_soon (bool | Unset):  Default: False.
        capability (None | str | Unset):
        available (bool | Unset):  Default: True.
        unavailable_reason (None | str | Unset):
    """

    name: str
    description: str
    parameters: list[ToolParameterPayload]
    hints: Hints
    description_i18n: DescriptionI18N | Unset = UNSET
    aliases: list[str] | Unset = UNSET
    toggleable: bool | Unset = False
    enabled: bool | Unset = True
    coming_soon: bool | Unset = False
    capability: None | str | Unset = UNSET
    available: bool | Unset = True
    unavailable_reason: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        description = self.description

        parameters = []
        for parameters_item_data in self.parameters:
            parameters_item = parameters_item_data.to_dict()
            parameters.append(parameters_item)

        hints = self.hints.to_dict()

        description_i18n: dict[str, Any] | Unset = UNSET
        if not isinstance(self.description_i18n, Unset):
            description_i18n = self.description_i18n.to_dict()

        aliases: list[str] | Unset = UNSET
        if not isinstance(self.aliases, Unset):
            aliases = self.aliases

        toggleable = self.toggleable

        enabled = self.enabled

        coming_soon = self.coming_soon

        capability: None | str | Unset
        if isinstance(self.capability, Unset):
            capability = UNSET
        else:
            capability = self.capability

        available = self.available

        unavailable_reason: None | str | Unset
        if isinstance(self.unavailable_reason, Unset):
            unavailable_reason = UNSET
        else:
            unavailable_reason = self.unavailable_reason

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "description": description,
                "parameters": parameters,
                "hints": hints,
            }
        )
        if description_i18n is not UNSET:
            field_dict["description_i18n"] = description_i18n
        if aliases is not UNSET:
            field_dict["aliases"] = aliases
        if toggleable is not UNSET:
            field_dict["toggleable"] = toggleable
        if enabled is not UNSET:
            field_dict["enabled"] = enabled
        if coming_soon is not UNSET:
            field_dict["coming_soon"] = coming_soon
        if capability is not UNSET:
            field_dict["capability"] = capability
        if available is not UNSET:
            field_dict["available"] = available
        if unavailable_reason is not UNSET:
            field_dict["unavailable_reason"] = unavailable_reason

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.description_i18n import DescriptionI18N  # noqa: PLC0415
        from ..models.hints import Hints  # noqa: PLC0415
        from ..models.tool_parameter_payload import ToolParameterPayload  # noqa: PLC0415

        d = dict(src_dict)
        name = d.pop("name")

        description = d.pop("description")

        parameters = []
        _parameters = d.pop("parameters")
        for parameters_item_data in _parameters:
            parameters_item = ToolParameterPayload.from_dict(parameters_item_data)

            parameters.append(parameters_item)

        hints = Hints.from_dict(d.pop("hints"))

        _description_i18n = d.pop("description_i18n", UNSET)
        description_i18n: DescriptionI18N | Unset
        if isinstance(_description_i18n, Unset):
            description_i18n = UNSET
        else:
            description_i18n = DescriptionI18N.from_dict(_description_i18n)

        aliases = cast(list[str], d.pop("aliases", UNSET))

        toggleable = d.pop("toggleable", UNSET)

        enabled = d.pop("enabled", UNSET)

        coming_soon = d.pop("coming_soon", UNSET)

        def _parse_capability(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        capability = _parse_capability(d.pop("capability", UNSET))

        available = d.pop("available", UNSET)

        def _parse_unavailable_reason(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        unavailable_reason = _parse_unavailable_reason(d.pop("unavailable_reason", UNSET))

        builtin_tool_payload = cls(
            name=name,
            description=description,
            parameters=parameters,
            hints=hints,
            description_i18n=description_i18n,
            aliases=aliases,
            toggleable=toggleable,
            enabled=enabled,
            coming_soon=coming_soon,
            capability=capability,
            available=available,
            unavailable_reason=unavailable_reason,
        )

        builtin_tool_payload.additional_properties = d
        return builtin_tool_payload

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
