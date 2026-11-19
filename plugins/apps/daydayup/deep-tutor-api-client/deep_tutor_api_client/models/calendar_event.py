from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.calendar_event_source import CalendarEventSource, check_calendar_event_source
from ..types import UNSET, Unset

T = TypeVar("T", bound="CalendarEvent")


@_attrs_define
class CalendarEvent:
    """A stored master or override row.

    Attributes:
        id (str):
        calendar_id (str):
        title (str):
        notes (str):
        location (str):
        all_day (bool):
        start (str):
        end (str):
        tzid (str):
        rrule (None | str):
        exdates (list[str]):
        reminders (list[int]):
        color (None | str):
        task_id (None | str):
        task_workspace_id (None | str):
        series_id (None | str):
        recurrence_id (None | str):
        created_at (str):
        updated_at (str):
        source (CalendarEventSource | Unset):  Default: 'user'.
    """

    id: str
    calendar_id: str
    title: str
    notes: str
    location: str
    all_day: bool
    start: str
    end: str
    tzid: str
    rrule: None | str
    exdates: list[str]
    reminders: list[int]
    color: None | str
    task_id: None | str
    task_workspace_id: None | str
    series_id: None | str
    recurrence_id: None | str
    created_at: str
    updated_at: str
    source: CalendarEventSource | Unset = "user"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

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

        exdates = self.exdates

        reminders = self.reminders

        color: None | str
        color = self.color

        task_id: None | str
        task_id = self.task_id

        task_workspace_id: None | str
        task_workspace_id = self.task_workspace_id

        series_id: None | str
        series_id = self.series_id

        recurrence_id: None | str
        recurrence_id = self.recurrence_id

        created_at = self.created_at

        updated_at = self.updated_at

        source: str | Unset = UNSET
        if not isinstance(self.source, Unset):
            source = self.source

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "calendar_id": calendar_id,
                "title": title,
                "notes": notes,
                "location": location,
                "all_day": all_day,
                "start": start,
                "end": end,
                "tzid": tzid,
                "rrule": rrule,
                "exdates": exdates,
                "reminders": reminders,
                "color": color,
                "task_id": task_id,
                "task_workspace_id": task_workspace_id,
                "series_id": series_id,
                "recurrence_id": recurrence_id,
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )
        if source is not UNSET:
            field_dict["source"] = source

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

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

        exdates = cast(list[str], d.pop("exdates"))

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

        def _parse_series_id(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        series_id = _parse_series_id(d.pop("series_id"))

        def _parse_recurrence_id(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        recurrence_id = _parse_recurrence_id(d.pop("recurrence_id"))

        created_at = d.pop("created_at")

        updated_at = d.pop("updated_at")

        _source = d.pop("source", UNSET)
        source: CalendarEventSource | Unset
        if isinstance(_source, Unset):
            source = UNSET
        else:
            source = check_calendar_event_source(_source)

        calendar_event = cls(
            id=id,
            calendar_id=calendar_id,
            title=title,
            notes=notes,
            location=location,
            all_day=all_day,
            start=start,
            end=end,
            tzid=tzid,
            rrule=rrule,
            exdates=exdates,
            reminders=reminders,
            color=color,
            task_id=task_id,
            task_workspace_id=task_workspace_id,
            series_id=series_id,
            recurrence_id=recurrence_id,
            created_at=created_at,
            updated_at=updated_at,
            source=source,
        )

        calendar_event.additional_properties = d
        return calendar_event

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
