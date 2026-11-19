from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="DailyUsage")


@_attrs_define
class DailyUsage:
    """
    Attributes:
        date (str):
        total_tokens (int | Unset):  Default: 0.
        total_calls (int | Unset):  Default: 0.
        turns (int | Unset):  Default: 0.
        tracked_turns (int | Unset):  Default: 0.
    """

    date: str
    total_tokens: int | Unset = 0
    total_calls: int | Unset = 0
    turns: int | Unset = 0
    tracked_turns: int | Unset = 0
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        date = self.date

        total_tokens = self.total_tokens

        total_calls = self.total_calls

        turns = self.turns

        tracked_turns = self.tracked_turns

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "date": date,
            }
        )
        if total_tokens is not UNSET:
            field_dict["total_tokens"] = total_tokens
        if total_calls is not UNSET:
            field_dict["total_calls"] = total_calls
        if turns is not UNSET:
            field_dict["turns"] = turns
        if tracked_turns is not UNSET:
            field_dict["tracked_turns"] = tracked_turns

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        date = d.pop("date")

        total_tokens = d.pop("total_tokens", UNSET)

        total_calls = d.pop("total_calls", UNSET)

        turns = d.pop("turns", UNSET)

        tracked_turns = d.pop("tracked_turns", UNSET)

        daily_usage = cls(
            date=date,
            total_tokens=total_tokens,
            total_calls=total_calls,
            turns=turns,
            tracked_turns=tracked_turns,
        )

        daily_usage.additional_properties = d
        return daily_usage

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
