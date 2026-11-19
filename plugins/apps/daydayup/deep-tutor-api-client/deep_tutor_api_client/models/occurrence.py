from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.occurrence_source import OccurrenceSource, check_occurrence_source
from ..types import UNSET, Unset

T = TypeVar("T", bound="Occurrence")


@_attrs_define
class Occurrence:
    """One rendered instance of a stored event.

    Attributes:
        id (str):
        event_id (str):
        series_id (None | str):
        occurrence (str):
        recurring (bool):
        calendar_id (str):
        title (str):
        notes (str):
        location (str):
        all_day (bool):
        start (str):
        end (str):
        tzid (str):
        rrule (None | str):
        reminders (list[int]):
        color (None | str):
        task_id (None | str):
        task_workspace_id (None | str):
        source (OccurrenceSource | Unset):  Default: 'user'.
        reminder_times (list[str] | Unset):
    """

    id: str
    event_id: str
    series_id: None | str
    occurrence: str
    recurring: bool
    calendar_id: str
    title: str
    notes: str
    location: str
    all_day: bool
    start: str
    end: str
    tzid: str
    rrule: None | str
    reminders: list[int]
    color: None | str
    task_id: None | str
    task_workspace_id: None | str
    source: OccurrenceSource | Unset = "user"
    reminder_times: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        event_id = self.event_id

        series_id: None | str
        series_id = self.series_id

        occurrence = self.occurrence

        recurring = self.recurring

        calendar_id = self.calendar_id

        title = self.title

        notes = self.notes

        location = self.location

        all_day = self.all_day

        start = self.start

        end = self.end

        tzid = self.tzid

        rrule: None | str
        rrule = self.rrule

        reminders = self.reminders

        color: None | str
        color = self.color

        task_id: None | str
        task_id = self.task_id

        task_workspace_id: None | str
        task_workspace_id = self.task_workspace_id

        source: str | Unset = UNSET
        if not isinstance(self.source, Unset):
            source = self.source

        reminder_times: list[str] | Unset = UNSET
        if not isinstance(self.reminder_times, Unset):
            reminder_times = self.reminder_times

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "event_id": event_id,
                "series_id": series_id,
                "occurrence": occurrence,
                "recurring": recurring,
                "calendar_id": calendar_id,
                "title": title,
                "notes": notes,
                "location": location,
                "all_day": all_day,
                "start": start,
                "end": end,
                "tzid": tzid,
                "rrule": rrule,
                "reminders": reminders,
                "color": color,
                "task_id": task_id,
                "task_workspace_id": task_workspace_id,
            }
        )
        if source is not UNSET:
            field_dict["source"] = source
        if reminder_times is not UNSET:
            field_dict["reminder_times"] = reminder_times

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        event_id = d.pop("event_id")

        def _parse_series_id(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        series_id = _parse_series_id(d.pop("series_id"))

        occurrence = d.pop("occurrence")

        recurring = d.pop("recurring")

        calendar_id = d.pop("calendar_id")

        title = d.pop("title")

        notes = d.pop("notes")

        location = d.pop("location")

        all_day = d.pop("all_day")

        start = d.pop("start")

        end = d.pop("end")

        tzid = d.pop("tzid")

        def _parse_rrule(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        rrule = _parse_rrule(d.pop("rrule"))

        reminders = cast(list[int], d.pop("reminders"))

        def _parse_color(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        color = _parse_color(d.pop("color"))

        def _parse_task_id(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        task_id = _parse_task_id(d.pop("task_id"))

        def _parse_task_workspace_id(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        task_workspace_id = _parse_task_workspace_id(d.pop("task_workspace_id"))

        _source = d.pop("source", UNSET)
        source: OccurrenceSource | Unset
        if isinstance(_source, Unset):
            source = UNSET
        else:
            source = check_occurrence_source(_source)

        reminder_times = cast(list[str], d.pop("reminder_times", UNSET))

        occurrence = cls(
            id=id,
            event_id=event_id,
            series_id=series_id,
            occurrence=occurrence,
            recurring=recurring,
            calendar_id=calendar_id,
            title=title,
            notes=notes,
            location=location,
            all_day=all_day,
            start=start,
            end=end,
            tzid=tzid,
            rrule=rrule,
            reminders=reminders,
            color=color,
            task_id=task_id,
            task_workspace_id=task_workspace_id,
            source=source,
            reminder_times=reminder_times,
        )

        occurrence.additional_properties = d
        return occurrence

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
