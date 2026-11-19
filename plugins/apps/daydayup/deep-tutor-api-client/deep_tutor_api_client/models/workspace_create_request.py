from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="WorkspaceCreateRequest")


@_attrs_define
class WorkspaceCreateRequest:
    """
    Attributes:
        title (str | Unset):  Default: 'Untitled collection'.
        description (str | Unset):  Default: ''.
        color (str | Unset):  Default: ''.
        material_ids (list[str] | Unset):
    """

    title: str | Unset = "Untitled collection"
    description: str | Unset = ""
    color: str | Unset = ""
    material_ids: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        title = self.title

        description = self.description

        color = self.color

        material_ids: list[str] | Unset = UNSET
        if not isinstance(self.material_ids, Unset):
            material_ids = self.material_ids

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if title is not UNSET:
            field_dict["title"] = title
        if description is not UNSET:
            field_dict["description"] = description
        if color is not UNSET:
            field_dict["color"] = color
        if material_ids is not UNSET:
            field_dict["material_ids"] = material_ids

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        title = d.pop("title", UNSET)

        description = d.pop("description", UNSET)

        color = d.pop("color", UNSET)

        material_ids = cast(list[str], d.pop("material_ids", UNSET))

        workspace_create_request = cls(
            title=title,
            description=description,
            color=color,
            material_ids=material_ids,
        )

        workspace_create_request.additional_properties = d
        return workspace_create_request

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
