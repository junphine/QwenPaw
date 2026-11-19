from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.calendar_event import CalendarEvent


T = TypeVar("T", bound="CalendarEventResponse")


@_attrs_define
class CalendarEventResponse:
    """
    Attributes:
        event (CalendarEvent): A stored master or override row.
        revision (int):
    """

    event: CalendarEvent
    revision: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        event = self.event.to_dict()

        revision = self.revision

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "event": event,
                "revision": revision,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.calendar_event import CalendarEvent  # noqa: PLC0415

        d = dict(src_dict)
        event = CalendarEvent.from_dict(d.pop("event"))

        revision = d.pop("revision")

        calendar_event_response = cls(
            event=event,
            revision=revision,
        )

        calendar_event_response.additional_properties = d
        return calendar_event_response

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
