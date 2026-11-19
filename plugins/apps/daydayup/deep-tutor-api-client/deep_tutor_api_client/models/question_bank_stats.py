from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="QuestionBankStats")


@_attrs_define
class QuestionBankStats:
    """
    Attributes:
        total (int | Unset):  Default: 0.
        wrong (int | Unset):  Default: 0.
        unresolved (int | Unset):  Default: 0.
        bookmarked (int | Unset):  Default: 0.
        uncategorized (int | Unset):  Default: 0.
    """

    total: int | Unset = 0
    wrong: int | Unset = 0
    unresolved: int | Unset = 0
    bookmarked: int | Unset = 0
    uncategorized: int | Unset = 0
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        total = self.total

        wrong = self.wrong

        unresolved = self.unresolved

        bookmarked = self.bookmarked

        uncategorized = self.uncategorized

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if total is not UNSET:
            field_dict["total"] = total
        if wrong is not UNSET:
            field_dict["wrong"] = wrong
        if unresolved is not UNSET:
            field_dict["unresolved"] = unresolved
        if bookmarked is not UNSET:
            field_dict["bookmarked"] = bookmarked
        if uncategorized is not UNSET:
            field_dict["uncategorized"] = uncategorized

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        total = d.pop("total", UNSET)

        wrong = d.pop("wrong", UNSET)

        unresolved = d.pop("unresolved", UNSET)

        bookmarked = d.pop("bookmarked", UNSET)

        uncategorized = d.pop("uncategorized", UNSET)

        question_bank_stats = cls(
            total=total,
            wrong=wrong,
            unresolved=unresolved,
            bookmarked=bookmarked,
            uncategorized=uncategorized,
        )

        question_bank_stats.additional_properties = d
        return question_bank_stats

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
