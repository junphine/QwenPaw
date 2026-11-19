from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.quiz_result_item_options_type_0 import QuizResultItemOptionsType0


T = TypeVar("T", bound="QuizResultItem")


@_attrs_define
class QuizResultItem:
    """
    Attributes:
        question (str):
        is_correct (bool):
        question_id (str | Unset):  Default: ''.
        question_type (str | Unset):  Default: ''.
        options (None | QuizResultItemOptionsType0 | Unset):
        user_answer (str | Unset):  Default: ''.
        correct_answer (str | Unset):  Default: ''.
        explanation (None | str | Unset):  Default: ''.
        difficulty (None | str | Unset):  Default: ''.
    """

    question: str
    is_correct: bool
    question_id: str | Unset = ""
    question_type: str | Unset = ""
    options: None | QuizResultItemOptionsType0 | Unset = UNSET
    user_answer: str | Unset = ""
    correct_answer: str | Unset = ""
    explanation: None | str | Unset = ""
    difficulty: None | str | Unset = ""
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.quiz_result_item_options_type_0 import QuizResultItemOptionsType0  # noqa: PLC0415

        question = self.question

        is_correct = self.is_correct

        question_id = self.question_id

        question_type = self.question_type

        options: dict[str, Any] | None | Unset
        if isinstance(self.options, Unset):
            options = UNSET
        elif isinstance(self.options, QuizResultItemOptionsType0):
            options = self.options.to_dict()
        else:
            options = self.options

        user_answer = self.user_answer

        correct_answer = self.correct_answer

        explanation: None | str | Unset
        if isinstance(self.explanation, Unset):
            explanation = UNSET
        else:
            explanation = self.explanation

        difficulty: None | str | Unset
        if isinstance(self.difficulty, Unset):
            difficulty = UNSET
        else:
            difficulty = self.difficulty

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "question": question,
                "is_correct": is_correct,
            }
        )
        if question_id is not UNSET:
            field_dict["question_id"] = question_id
        if question_type is not UNSET:
            field_dict["question_type"] = question_type
        if options is not UNSET:
            field_dict["options"] = options
        if user_answer is not UNSET:
            field_dict["user_answer"] = user_answer
        if correct_answer is not UNSET:
            field_dict["correct_answer"] = correct_answer
        if explanation is not UNSET:
            field_dict["explanation"] = explanation
        if difficulty is not UNSET:
            field_dict["difficulty"] = difficulty

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.quiz_result_item_options_type_0 import QuizResultItemOptionsType0  # noqa: PLC0415

        d = dict(src_dict)
        question = d.pop("question")

        is_correct = d.pop("is_correct")

        question_id = d.pop("question_id", UNSET)

        question_type = d.pop("question_type", UNSET)

        def _parse_options(data: object) -> None | QuizResultItemOptionsType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                options_type_0 = QuizResultItemOptionsType0.from_dict(data)

                return options_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | QuizResultItemOptionsType0 | Unset, data)

        options = _parse_options(d.pop("options", UNSET))

        user_answer = d.pop("user_answer", UNSET)

        correct_answer = d.pop("correct_answer", UNSET)

        def _parse_explanation(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        explanation = _parse_explanation(d.pop("explanation", UNSET))

        def _parse_difficulty(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        difficulty = _parse_difficulty(d.pop("difficulty", UNSET))

        quiz_result_item = cls(
            question=question,
            is_correct=is_correct,
            question_id=question_id,
            question_type=question_type,
            options=options,
            user_answer=user_answer,
            correct_answer=correct_answer,
            explanation=explanation,
            difficulty=difficulty,
        )

        quiz_result_item.additional_properties = d
        return quiz_result_item

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
