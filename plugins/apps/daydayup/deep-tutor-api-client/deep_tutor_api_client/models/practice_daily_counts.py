from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="PracticeDailyCounts")


@_attrs_define
class PracticeDailyCounts:
    """
    Attributes:
        questions (int):
        mistakes (int):
        reviews (int):
        date (str):
    """

    questions: int
    mistakes: int
    reviews: int
    date: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        questions = self.questions

        mistakes = self.mistakes

        reviews = self.reviews

        date = self.date

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "questions": questions,
                "mistakes": mistakes,
                "reviews": reviews,
                "date": date,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        questions = d.pop("questions")

        mistakes = d.pop("mistakes")

        reviews = d.pop("reviews")

        date = d.pop("date")

        practice_daily_counts = cls(
            questions=questions,
            mistakes=mistakes,
            reviews=reviews,
            date=date,
        )

        practice_daily_counts.additional_properties = d
        return practice_daily_counts

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
