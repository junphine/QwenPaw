from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.subagent_settings_payload_backends_type_0 import SubagentSettingsPayloadBackendsType0


T = TypeVar("T", bound="SubagentSettingsPayload")


@_attrs_define
class SubagentSettingsPayload:
    """
    Attributes:
        consult_budget (int | None | Unset):
        backends (None | SubagentSettingsPayloadBackendsType0 | Unset):
    """

    consult_budget: int | None | Unset = UNSET
    backends: None | SubagentSettingsPayloadBackendsType0 | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.subagent_settings_payload_backends_type_0 import (
            SubagentSettingsPayloadBackendsType0,  # noqa: PLC0415
        )

        consult_budget: int | None | Unset
        if isinstance(self.consult_budget, Unset):
            consult_budget = UNSET
        else:
            consult_budget = self.consult_budget

        backends: dict[str, Any] | None | Unset
        if isinstance(self.backends, Unset):
            backends = UNSET
        elif isinstance(self.backends, SubagentSettingsPayloadBackendsType0):
            backends = self.backends.to_dict()
        else:
            backends = self.backends

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if consult_budget is not UNSET:
            field_dict["consult_budget"] = consult_budget
        if backends is not UNSET:
            field_dict["backends"] = backends

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.subagent_settings_payload_backends_type_0 import (
            SubagentSettingsPayloadBackendsType0,  # noqa: PLC0415
        )

        d = dict(src_dict)

        def _parse_consult_budget(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        consult_budget = _parse_consult_budget(d.pop("consult_budget", UNSET))

        def _parse_backends(data: object) -> None | SubagentSettingsPayloadBackendsType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                backends_type_0 = SubagentSettingsPayloadBackendsType0.from_dict(data)

                return backends_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | SubagentSettingsPayloadBackendsType0 | Unset, data)

        backends = _parse_backends(d.pop("backends", UNSET))

        subagent_settings_payload = cls(
            consult_budget=consult_budget,
            backends=backends,
        )

        subagent_settings_payload.additional_properties = d
        return subagent_settings_payload

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
