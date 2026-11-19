from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.review_path_count import ReviewPathCount


T = TypeVar("T", bound="ReviewDay")


@_attrs_define
class ReviewDay:
    """
    Attributes:
        date (str):
        mastery (int | Unset):  Default: 0.
        practice (int | Unset):  Default: 0.
        paths (list[ReviewPathCount] | Unset):
    """

    date: str
    mastery: int | Unset = 0
    practice: int | Unset = 0
    paths: list[ReviewPathCount] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        date = self.date

        mastery = self.mastery

        practice = self.practice

        paths: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.paths, Unset):
            paths = []
            for paths_item_data in self.paths:
                paths_item = paths_item_data.to_dict()
                paths.append(paths_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "date": date,
            }
        )
        if mastery is not UNSET:
            field_dict["mastery"] = mastery
        if practice is not UNSET:
            field_dict["practice"] = practice
        if paths is not UNSET:
            field_dict["paths"] = paths

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.review_path_count import ReviewPathCount  # noqa: PLC0415

        d = dict(src_dict)
        date = d.pop("date")

        mastery = d.pop("mastery", UNSET)

        practice = d.pop("practice", UNSET)

        _paths = d.pop("paths", UNSET)
        paths: list[ReviewPathCount] | Unset = UNSET
        if _paths is not UNSET:
            paths = []
            for paths_item_data in _paths:
                paths_item = ReviewPathCount.from_dict(paths_item_data)

                paths.append(paths_item)

        review_day = cls(
            date=date,
            mastery=mastery,
            practice=practice,
            paths=paths,
        )

        review_day.additional_properties = d
        return review_day

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
