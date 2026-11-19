from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="WorkspaceMaterialRequest")


@_attrs_define
class WorkspaceMaterialRequest:
    """
    Attributes:
        material_id (str):
        make_active (bool | Unset):  Default: False.
    """

    material_id: str
    make_active: bool | Unset = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        material_id = self.material_id

        make_active = self.make_active

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "material_id": material_id,
            }
        )
        if make_active is not UNSET:
            field_dict["make_active"] = make_active

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        material_id = d.pop("material_id")

        make_active = d.pop("make_active", UNSET)

        workspace_material_request = cls(
            material_id=material_id,
            make_active=make_active,
        )

        workspace_material_request.additional_properties = d
        return workspace_material_request

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
