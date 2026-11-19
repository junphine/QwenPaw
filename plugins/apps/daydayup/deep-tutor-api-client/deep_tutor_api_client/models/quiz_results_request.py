from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.quiz_result_item import QuizResultItem


T = TypeVar("T", bound="QuizResultsRequest")


@_attrs_define
class QuizResultsRequest:
    """
    Attributes:
        answers (list[QuizResultItem] | Unset):
        turn_id (str | Unset):  Default: ''.
    """

    answers: list[QuizResultItem] | Unset = UNSET
    turn_id: str | Unset = ""
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        answers: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.answers, Unset):
            answers = []
            for answers_item_data in self.answers:
                answers_item = answers_item_data.to_dict()
                answers.append(answers_item)

        turn_id = self.turn_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if answers is not UNSET:
            field_dict["answers"] = answers
        if turn_id is not UNSET:
            field_dict["turn_id"] = turn_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.quiz_result_item import QuizResultItem  # noqa: PLC0415

        d = dict(src_dict)
        _answers = d.pop("answers", UNSET)
        answers: list[QuizResultItem] | Unset = UNSET
        if _answers is not UNSET:
            answers = []
            for answers_item_data in _answers:
                answers_item = QuizResultItem.from_dict(answers_item_data)

                answers.append(answers_item)

        turn_id = d.pop("turn_id", UNSET)

        quiz_results_request = cls(
            answers=answers,
            turn_id=turn_id,
        )

        quiz_results_request.additional_properties = d
        return quiz_results_request

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
