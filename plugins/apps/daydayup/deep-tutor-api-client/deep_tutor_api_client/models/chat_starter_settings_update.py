from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ChatStarterSettingsUpdate")


@_attrs_define
class ChatStarterSettingsUpdate:
    """How much recent activity shapes the home screen's starting points, and
    whether the chat composer offers a predicted next line.

    Bounds mirror ``starter_settings.TRACE_COUNT_RANGE`` so the API rejects
    loudly what the file layer would silently clamp. ``ask_hint_enabled`` left
    out (``None``) keeps the stored value, so a client that only knows
    ``trace_count`` cannot switch the hint back on by accident.

        Attributes:
            trace_count (int):
            ask_hint_enabled (bool | None | Unset):
    """

    trace_count: int
    ask_hint_enabled: bool | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        trace_count = self.trace_count

        ask_hint_enabled: bool | None | Unset
        if isinstance(self.ask_hint_enabled, Unset):
            ask_hint_enabled = UNSET
        else:
            ask_hint_enabled = self.ask_hint_enabled

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "trace_count": trace_count,
            }
        )
        if ask_hint_enabled is not UNSET:
            field_dict["ask_hint_enabled"] = ask_hint_enabled

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        trace_count = d.pop("trace_count")

        def _parse_ask_hint_enabled(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        ask_hint_enabled = _parse_ask_hint_enabled(d.pop("ask_hint_enabled", UNSET))

        chat_starter_settings_update = cls(
            trace_count=trace_count,
            ask_hint_enabled=ask_hint_enabled,
        )

        chat_starter_settings_update.additional_properties = d
        return chat_starter_settings_update

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
