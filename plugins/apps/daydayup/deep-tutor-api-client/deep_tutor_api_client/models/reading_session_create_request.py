from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ReadingSessionCreateRequest")


@_attrs_define
class ReadingSessionCreateRequest:
    """
    Attributes:
        title (str | Unset):  Default: 'New reading conversation'.
        active_material_id (str | Unset):  Default: ''.
    """

    title: str | Unset = "New reading conversation"
    active_material_id: str | Unset = ""
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        title = self.title

        active_material_id = self.active_material_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if title is not UNSET:
            field_dict["title"] = title
        if active_material_id is not UNSET:
            field_dict["active_material_id"] = active_material_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        title = d.pop("title", UNSET)

        active_material_id = d.pop("active_material_id", UNSET)

        reading_session_create_request = cls(
            title=title,
            active_material_id=active_material_id,
        )

        reading_session_create_request.additional_properties = d
        return reading_session_create_request

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
