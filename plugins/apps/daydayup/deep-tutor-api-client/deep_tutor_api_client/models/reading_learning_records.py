from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.reading_activity_record import ReadingActivityRecord
    from ..models.reading_progress_record import ReadingProgressRecord


T = TypeVar("T", bound="ReadingLearningRecords")


@_attrs_define
class ReadingLearningRecords:
    """Account-scoped Reading summary for reporting surfaces.

    Attributes:
        progress (list[ReadingProgressRecord] | Unset):
        activities (list[ReadingActivityRecord] | Unset):
    """

    progress: list[ReadingProgressRecord] | Unset = UNSET
    activities: list[ReadingActivityRecord] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        progress: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.progress, Unset):
            progress = []
            for progress_item_data in self.progress:
                progress_item = progress_item_data.to_dict()
                progress.append(progress_item)

        activities: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.activities, Unset):
            activities = []
            for activities_item_data in self.activities:
                activities_item = activities_item_data.to_dict()
                activities.append(activities_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if progress is not UNSET:
            field_dict["progress"] = progress
        if activities is not UNSET:
            field_dict["activities"] = activities

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.reading_activity_record import ReadingActivityRecord  # noqa: PLC0415
        from ..models.reading_progress_record import ReadingProgressRecord  # noqa: PLC0415

        d = dict(src_dict)
        _progress = d.pop("progress", UNSET)
        progress: list[ReadingProgressRecord] | Unset = UNSET
        if _progress is not UNSET:
            progress = []
            for progress_item_data in _progress:
                progress_item = ReadingProgressRecord.from_dict(progress_item_data)

                progress.append(progress_item)

        _activities = d.pop("activities", UNSET)
        activities: list[ReadingActivityRecord] | Unset = UNSET
        if _activities is not UNSET:
            activities = []
            for activities_item_data in _activities:
                activities_item = ReadingActivityRecord.from_dict(activities_item_data)

                activities.append(activities_item)

        reading_learning_records = cls(
            progress=progress,
            activities=activities,
        )

        reading_learning_records.additional_properties = d
        return reading_learning_records

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
