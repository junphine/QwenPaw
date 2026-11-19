from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.practice_counts import PracticeCounts
    from ..models.practice_daily_counts import PracticeDailyCounts
    from ..models.practice_source_counts import PracticeSourceCounts


T = TypeVar("T", bound="PracticeAnalytics")


@_attrs_define
class PracticeAnalytics:
    """
    Attributes:
        timezone (str):
        days (int):
        start_date (str):
        end_date (str):
        updated_at (float):
        daily (list[PracticeDailyCounts]):
        sources (list[PracticeSourceCounts]):
        totals (PracticeCounts):
    """

    timezone: str
    days: int
    start_date: str
    end_date: str
    updated_at: float
    daily: list[PracticeDailyCounts]
    sources: list[PracticeSourceCounts]
    totals: PracticeCounts
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        timezone = self.timezone

        days = self.days

        start_date = self.start_date

        end_date = self.end_date

        updated_at = self.updated_at

        daily = []
        for daily_item_data in self.daily:
            daily_item = daily_item_data.to_dict()
            daily.append(daily_item)

        sources = []
        for sources_item_data in self.sources:
            sources_item = sources_item_data.to_dict()
            sources.append(sources_item)

        totals = self.totals.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "timezone": timezone,
                "days": days,
                "start_date": start_date,
                "end_date": end_date,
                "updated_at": updated_at,
                "daily": daily,
                "sources": sources,
                "totals": totals,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.practice_counts import PracticeCounts  # noqa: PLC0415
        from ..models.practice_daily_counts import PracticeDailyCounts  # noqa: PLC0415
        from ..models.practice_source_counts import PracticeSourceCounts  # noqa: PLC0415

        d = dict(src_dict)
        timezone = d.pop("timezone")

        days = d.pop("days")

        start_date = d.pop("start_date")

        end_date = d.pop("end_date")

        updated_at = d.pop("updated_at")

        daily = []
        _daily = d.pop("daily")
        for daily_item_data in _daily:
            daily_item = PracticeDailyCounts.from_dict(daily_item_data)

            daily.append(daily_item)

        sources = []
        _sources = d.pop("sources")
        for sources_item_data in _sources:
            sources_item = PracticeSourceCounts.from_dict(sources_item_data)

            sources.append(sources_item)

        totals = PracticeCounts.from_dict(d.pop("totals"))

        practice_analytics = cls(
            timezone=timezone,
            days=days,
            start_date=start_date,
            end_date=end_date,
            updated_at=updated_at,
            daily=daily,
            sources=sources,
            totals=totals,
        )

        practice_analytics.additional_properties = d
        return practice_analytics

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
