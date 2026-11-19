from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.review_request_rating import ReviewRequestRating, check_review_request_rating
from ..types import UNSET, Unset

T = TypeVar("T", bound="ReviewRequest")


@_attrs_define
class ReviewRequest:
    """
    Attributes:
        request_id (str):
        version (int):
        rating (ReviewRequestRating):
        answer (str | Unset):  Default: ''.
        self_report (bool | Unset):  Default: False.
    """

    request_id: str
    version: int
    rating: ReviewRequestRating
    answer: str | Unset = ""
    self_report: bool | Unset = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        request_id = self.request_id

        version = self.version

        rating: str = self.rating

        answer = self.answer

        self_report = self.self_report

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "request_id": request_id,
                "version": version,
                "rating": rating,
            }
        )
        if answer is not UNSET:
            field_dict["answer"] = answer
        if self_report is not UNSET:
            field_dict["self_report"] = self_report

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        request_id = d.pop("request_id")

        version = d.pop("version")

        rating = check_review_request_rating(d.pop("rating"))

        answer = d.pop("answer", UNSET)

        self_report = d.pop("self_report", UNSET)

        review_request = cls(
            request_id=request_id,
            version=version,
            rating=rating,
            answer=answer,
            self_report=self_report,
        )

        review_request.additional_properties = d
        return review_request

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
