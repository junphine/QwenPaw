from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GenerateFromReadingRequest")


@_attrs_define
class GenerateFromReadingRequest:
    """
    Attributes:
        workspace_id (str):
        material_ids (list[str] | Unset):
    """

    workspace_id: str
    material_ids: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        workspace_id = self.workspace_id

        material_ids: list[str] | Unset = UNSET
        if not isinstance(self.material_ids, Unset):
            material_ids = self.material_ids

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "workspace_id": workspace_id,
            }
        )
        if material_ids is not UNSET:
            field_dict["material_ids"] = material_ids

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        workspace_id = d.pop("workspace_id")

        material_ids = cast(list[str], d.pop("material_ids", UNSET))

        generate_from_reading_request = cls(
            workspace_id=workspace_id,
            material_ids=material_ids,
        )

        generate_from_reading_request.additional_properties = d
        return generate_from_reading_request

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
