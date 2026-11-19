from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ReadingProgressRecord")


@_attrs_define
class ReadingProgressRecord:
    """One material's Reading progress in an account's learning records.

    Attributes:
        material_id (str):
        latest_locator (int):
        latest_percentage (float):
        furthest_locator (int):
        furthest_percentage (float):
        updated_at (float | Unset):
    """

    material_id: str
    latest_locator: int
    latest_percentage: float
    furthest_locator: int
    furthest_percentage: float
    updated_at: float | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        material_id = self.material_id

        latest_locator = self.latest_locator

        latest_percentage = self.latest_percentage

        furthest_locator = self.furthest_locator

        furthest_percentage = self.furthest_percentage

        updated_at = self.updated_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "material_id": material_id,
                "latest_locator": latest_locator,
                "latest_percentage": latest_percentage,
                "furthest_locator": furthest_locator,
                "furthest_percentage": furthest_percentage,
            }
        )
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        material_id = d.pop("material_id")

        latest_locator = d.pop("latest_locator")

        latest_percentage = d.pop("latest_percentage")

        furthest_locator = d.pop("furthest_locator")

        furthest_percentage = d.pop("furthest_percentage")

        updated_at = d.pop("updated_at", UNSET)

        reading_progress_record = cls(
            material_id=material_id,
            latest_locator=latest_locator,
            latest_percentage=latest_percentage,
            furthest_locator=furthest_locator,
            furthest_percentage=furthest_percentage,
            updated_at=updated_at,
        )

        reading_progress_record.additional_properties = d
        return reading_progress_record

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
