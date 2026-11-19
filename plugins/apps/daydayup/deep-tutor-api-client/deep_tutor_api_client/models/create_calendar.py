from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="CreateCalendar")


@_attrs_define
class CreateCalendar:
    """
    Attributes:
        name (str):
        color (str):
    """

    name: str
    color: str

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        color = self.color

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "name": name,
                "color": color,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        color = d.pop("color")

        create_calendar = cls(
            name=name,
            color=color,
        )

        return create_calendar
