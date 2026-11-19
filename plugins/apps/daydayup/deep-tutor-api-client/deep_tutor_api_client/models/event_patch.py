from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="EventPatch")


@_attrs_define
class EventPatch:
    """Every field optional; explicit null clears rrule/color/task links only.

    Attributes:
        calendar_id (None | str | Unset):
        title (None | str | Unset):
        notes (None | str | Unset):
        location (None | str | Unset):
        all_day (bool | None | Unset):
        start (None | str | Unset):
        end (None | str | Unset):
        tzid (None | str | Unset):
        rrule (None | str | Unset):
        reminders (list[int] | None | Unset):
        color (None | str | Unset):
        task_id (None | str | Unset):
        task_workspace_id (None | str | Unset):
    """

    calendar_id: None | str | Unset = UNSET
    title: None | str | Unset = UNSET
    notes: None | str | Unset = UNSET
    location: None | str | Unset = UNSET
    all_day: bool | None | Unset = UNSET
    start: None | str | Unset = UNSET
    end: None | str | Unset = UNSET
    tzid: None | str | Unset = UNSET
    rrule: None | str | Unset = UNSET
    reminders: list[int] | None | Unset = UNSET
    color: None | str | Unset = UNSET
    task_id: None | str | Unset = UNSET
    task_workspace_id: None | str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        calendar_id: None | str | Unset
        if isinstance(self.calendar_id, Unset):
            calendar_id = UNSET
        else:
            calendar_id = self.calendar_id

        title: None | str | Unset
        if isinstance(self.title, Unset):
            title = UNSET
        else:
            title = self.title

        notes: None | str | Unset
        if isinstance(self.notes, Unset):
            notes = UNSET
        else:
            notes = self.notes

        location: None | str | Unset
        if isinstance(self.location, Unset):
            location = UNSET
        else:
            location = self.location

        all_day: bool | None | Unset
        if isinstance(self.all_day, Unset):
            all_day = UNSET
        else:
            all_day = self.all_day

        start: None | str | Unset
        if isinstance(self.start, Unset):
            start = UNSET
        else:
            start = self.start

        end: None | str | Unset
        if isinstance(self.end, Unset):
            end = UNSET
        else:
            end = self.end

        tzid: None | str | Unset
        if isinstance(self.tzid, Unset):
            tzid = UNSET
        else:
            tzid = self.tzid

        rrule: None | str | Unset
        if isinstance(self.rrule, Unset):
            rrule = UNSET
        else:
            rrule = self.rrule

        reminders: list[int] | None | Unset
        if isinstance(self.reminders, Unset):
            reminders = UNSET
        elif isinstance(self.reminders, list):
            reminders = self.reminders

        else:
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

        field_dict.update({})
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
        if start is not UNSET:
            field_dict["start"] = start
        if end is not UNSET:
            field_dict["end"] = end
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

        def _parse_calendar_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        calendar_id = _parse_calendar_id(d.pop("calendar_id", UNSET))

        def _parse_title(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        title = _parse_title(d.pop("title", UNSET))

        def _parse_notes(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        notes = _parse_notes(d.pop("notes", UNSET))

        def _parse_location(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        location = _parse_location(d.pop("location", UNSET))

        def _parse_all_day(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        all_day = _parse_all_day(d.pop("all_day", UNSET))

        def _parse_start(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        start = _parse_start(d.pop("start", UNSET))

        def _parse_end(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        end = _parse_end(d.pop("end", UNSET))

        def _parse_tzid(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        tzid = _parse_tzid(d.pop("tzid", UNSET))

        def _parse_rrule(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        rrule = _parse_rrule(d.pop("rrule", UNSET))

        def _parse_reminders(data: object) -> list[int] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                reminders_type_0 = cast(list[int], data)

                return reminders_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[int] | None | Unset, data)

        reminders = _parse_reminders(d.pop("reminders", UNSET))

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

        event_patch = cls(
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
        )

        return event_patch
