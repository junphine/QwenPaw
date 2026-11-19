from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="PracticeSummary")


@_attrs_define
class PracticeSummary:
    """
    Attributes:
        total (int):
        mistakes (int):
        due (int):
        overdue (int):
        reviewed_today (int):
        next_due_at (float | None):
        day_end (float):
        timezone (str):
    """

    total: int
    mistakes: int
    due: int
    overdue: int
    reviewed_today: int
    next_due_at: float | None
    day_end: float
    timezone: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        total = self.total

        mistakes = self.mistakes

        due = self.due

        overdue = self.overdue

        reviewed_today = self.reviewed_today

        next_due_at: float | None
        next_due_at = self.next_due_at

        day_end = self.day_end

        timezone = self.timezone

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "total": total,
                "mistakes": mistakes,
                "due": due,
                "overdue": overdue,
                "reviewed_today": reviewed_today,
                "next_due_at": next_due_at,
                "day_end": day_end,
                "timezone": timezone,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        total = d.pop("total")

        mistakes = d.pop("mistakes")

        due = d.pop("due")

        overdue = d.pop("overdue")

        reviewed_today = d.pop("reviewed_today")

        def _parse_next_due_at(data: object) -> float | None:
            if data is None:
                return data
            return cast(float | None, data)

        next_due_at = _parse_next_due_at(d.pop("next_due_at"))

        day_end = d.pop("day_end")

        timezone = d.pop("timezone")

        practice_summary = cls(
            total=total,
            mistakes=mistakes,
            due=due,
            overdue=overdue,
            reviewed_today=reviewed_today,
            next_due_at=next_due_at,
            day_end=day_end,
            timezone=timezone,
        )

        practice_summary.additional_properties = d
        return practice_summary

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
