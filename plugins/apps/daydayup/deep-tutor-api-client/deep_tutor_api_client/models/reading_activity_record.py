from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.reading_activity_record_result_type import (
    ReadingActivityRecordResultType,
    check_reading_activity_record_result_type,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="ReadingActivityRecord")


@_attrs_define
class ReadingActivityRecord:
    """One successful Reading-extension action, without source content.

    Attributes:
        activity_id (str):
        material_id (str):
        extension_id (str):
        action (str):
        locator (int):
        result_type (ReadingActivityRecordResultType):
        created_at (float | Unset):
    """

    activity_id: str
    material_id: str
    extension_id: str
    action: str
    locator: int
    result_type: ReadingActivityRecordResultType
    created_at: float | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        activity_id = self.activity_id

        material_id = self.material_id

        extension_id = self.extension_id

        action = self.action

        locator = self.locator

        result_type: str = self.result_type

        created_at = self.created_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "activity_id": activity_id,
                "material_id": material_id,
                "extension_id": extension_id,
                "action": action,
                "locator": locator,
                "result_type": result_type,
            }
        )
        if created_at is not UNSET:
            field_dict["created_at"] = created_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        activity_id = d.pop("activity_id")

        material_id = d.pop("material_id")

        extension_id = d.pop("extension_id")

        action = d.pop("action")

        locator = d.pop("locator")

        result_type = check_reading_activity_record_result_type(d.pop("result_type"))

        created_at = d.pop("created_at", UNSET)

        reading_activity_record = cls(
            activity_id=activity_id,
            material_id=material_id,
            extension_id=extension_id,
            action=action,
            locator=locator,
            result_type=result_type,
            created_at=created_at,
        )

        reading_activity_record.additional_properties = d
        return reading_activity_record

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
