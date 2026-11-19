from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="EventInput")


@_attrs_define
class EventInput:
    """A new event, or the merged result of a patch before it is stored.

    Attributes:
        start (str):
        end (str):
        calendar_id (None | str | Unset):
        title (str | Unset):  Default: ''.
        notes (str | Unset):  Default: ''.
        location (str | Unset):  Default: ''.
        all_day (bool | Unset):  Default: False.
        tzid (str | Unset):  Default: 'UTC'.
        rrule (None | str | Unset):
        reminders (list[int] | Unset):
        color (None | str | Unset):
        task_id (None | str | Unset):
        task_workspace_id (None | str | Unset):
    """

    start: str
    end: str
    calendar_id: None | str | Unset = UNSET
    title: str | Unset = ""
    notes: str | Unset = ""
    location: str | Unset = ""
    all_day: bool | Unset = False
    tzid: str | Unset = "UTC"
    rrule: None | str | Unset = UNSET
    reminders: list[int] | Unset = UNSET
    color: None | str | Unset = UNSET
    task_id: None | str | Unset = UNSET
    task_workspace_id: None | str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        start = self.start

        end = self.end

        calendar_id: None | str | Unset
        if isinstance(self.calendar_id, Unset):
            calendar_id = UNSET
        else:
            calendar_id = self.calendar_id

        title = self.title

        notes = self.notes

        location = self.location

        all_day = self.all_day

        tzid = self.tzid

        rrule: None | str | Unset
        if isinstance(self.rrule, Unset):
            rrule = UNSET
        else:
            rrule = self.rrule

        reminders: list[int] | Unset = UNSET
        if not isinstance(self.reminders, Unset):
            reminders = self.reminders

        color: None | str | Unset
        if isinstance(self.color, Unset):
            color = UNSET
        else:
            color = self.color

        task_id: None | str | Unset
        if isinstance(self.task_id, Unset):
            task_id = UNSET
        else:
            task_id = self.task_id

        task_workspace_id: None | str | Unset
        if isinstance(self.task_workspace_id, Unset):
            task_workspace_id = UNSET
        else:
            task_workspace_id = self.task_workspace_id

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "start": start,
                "end": end,
            }
        )
        if calendar_id is not UNSET:
            field_dict["calendar_id"] = calendar_id
        if title is not UNSET:
            field_dict["title"] = title
        if notes is not UNSET:
            field_dict["notes"] = notes
        if location is not UNSET:
            field_dict["location"] = location
        if all_day is not UNSET:
            field_dict["all_day"] = all_day
        if tzid is not UNSET:
            field_dict["tzid"] = tzid
        if rrule is not UNSET:
            field_dict["rrule"] = rrule
        if reminders is not UNSET:
            field_dict["reminders"] = reminders
        if color is not UNSET:
            field_dict["color"] = color
        if task_id is not UNSET:
            field_dict["task_id"] = task_id
        if task_workspace_id is not UNSET:
            field_dict["task_workspace_id"] = task_workspace_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        start = d.pop("start")

        end = d.pop("end")

        def _parse_calendar_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        calendar_id = _parse_calendar_id(d.pop("calendar_id", UNSET))

        title = d.pop("title", UNSET)

        notes = d.pop("notes", UNSET)

        location = d.pop("location", UNSET)

        all_day = d.pop("all_day", UNSET)

        tzid = d.pop("tzid", UNSET)

        def _parse_rrule(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        rrule = _parse_rrule(d.pop("rrule", UNSET))

        reminders = cast(list[int], d.pop("reminders", UNSET))

        def _parse_color(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        color = _parse_color(d.pop("color", UNSET))

        def _parse_task_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        task_id = _parse_task_id(d.pop("task_id", UNSET))

        def _parse_task_workspace_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        task_workspace_id = _parse_task_workspace_id(d.pop("task_workspace_id", UNSET))

        event_input = cls(
            start=start,
            end=end,
            calendar_id=calendar_id,
            title=title,
            notes=notes,
            location=location,
            all_day=all_day,
            tzid=tzid,
            rrule=rrule,
            reminders=reminders,
            color=color,
            task_id=task_id,
            task_workspace_id=task_workspace_id,
        )

        return event_input
