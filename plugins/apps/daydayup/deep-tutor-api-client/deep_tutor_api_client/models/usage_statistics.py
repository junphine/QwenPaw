from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.daily_usage import DailyUsage
    from ..models.model_usage import ModelUsage
    from ..models.usage_totals import UsageTotals


T = TypeVar("T", bound="UsageStatistics")


@_attrs_define
class UsageStatistics:
    """
    Attributes:
        year (int):
        timezone (str):
        totals (UsageTotals):
        days (list[DailyUsage]):
        models (list[ModelUsage]):
        active_days (int):
        sessions (int):
        turns (int):
        tracked_turns (int):
        updated_at (float):
    """

    year: int
    timezone: str
    totals: UsageTotals
    days: list[DailyUsage]
    models: list[ModelUsage]
    active_days: int
    sessions: int
    turns: int
    tracked_turns: int
    updated_at: float
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        year = self.year

        timezone = self.timezone

        totals = self.totals.to_dict()

        days = []
        for days_item_data in self.days:
            days_item = days_item_data.to_dict()
            days.append(days_item)

        models = []
        for models_item_data in self.models:
            models_item = models_item_data.to_dict()
            models.append(models_item)

        active_days = self.active_days

        sessions = self.sessions

        turns = self.turns

        tracked_turns = self.tracked_turns

        updated_at = self.updated_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "year": year,
                "timezone": timezone,
                "totals": totals,
                "days": days,
                "models": models,
                "active_days": active_days,
                "sessions": sessions,
                "turns": turns,
                "tracked_turns": tracked_turns,
                "updated_at": updated_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.daily_usage import DailyUsage  # noqa: PLC0415
        from ..models.model_usage import ModelUsage  # noqa: PLC0415
        from ..models.usage_totals import UsageTotals  # noqa: PLC0415

        d = dict(src_dict)
        year = d.pop("year")

        timezone = d.pop("timezone")

        totals = UsageTotals.from_dict(d.pop("totals"))

        days = []
        _days = d.pop("days")
        for days_item_data in _days:
            days_item = DailyUsage.from_dict(days_item_data)

            days.append(days_item)

        models = []
        _models = d.pop("models")
        for models_item_data in _models:
            models_item = ModelUsage.from_dict(models_item_data)

            models.append(models_item)

        active_days = d.pop("active_days")

        sessions = d.pop("sessions")

        turns = d.pop("turns")

        tracked_turns = d.pop("tracked_turns")

        updated_at = d.pop("updated_at")

        usage_statistics = cls(
            year=year,
            timezone=timezone,
            totals=totals,
            days=days,
            models=models,
            active_days=active_days,
            sessions=sessions,
            turns=turns,
            tracked_turns=tracked_turns,
            updated_at=updated_at,
        )

        usage_statistics.additional_properties = d
        return usage_statistics

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
