from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="CalendarEntry")


@_attrs_define
class CalendarEntry:
    """
    Attributes:
        id (str):
        name (str):
        color (str):
        visible (bool):
        position (int):
        is_default (bool):
        created_at (str):
        updated_at (str):
    """

    id: str
    name: str
    color: str
    visible: bool
    position: int
    is_default: bool
    created_at: str
    updated_at: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        color = self.color

        visible = self.visible

        position = self.position

        is_default = self.is_default

        created_at = self.created_at

        updated_at = self.updated_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "color": color,
                "visible": visible,
                "position": position,
                "is_default": is_default,
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        color = d.pop("color")

        visible = d.pop("visible")

        position = d.pop("position")

        is_default = d.pop("is_default")

        created_at = d.pop("created_at")

        updated_at = d.pop("updated_at")

        calendar_entry = cls(
            id=id,
            name=name,
            color=color,
            visible=visible,
            position=position,
            is_default=is_default,
            created_at=created_at,
            updated_at=updated_at,
        )

        calendar_entry.additional_properties = d
        return calendar_entry

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
