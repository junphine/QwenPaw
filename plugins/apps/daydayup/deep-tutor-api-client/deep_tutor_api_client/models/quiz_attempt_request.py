from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="QuizAttemptRequest")


@_attrs_define
class QuizAttemptRequest:
    """
    Attributes:
        book_id (str):
        page_id (str):
        block_id (str):
        question_id (str | Unset):  Default: ''.
        user_answer (str | Unset):  Default: ''.
        is_correct (bool | None | Unset):
        submission_id (str | Unset):  Default: ''.
    """

    book_id: str
    page_id: str
    block_id: str
    question_id: str | Unset = ""
    user_answer: str | Unset = ""
    is_correct: bool | None | Unset = UNSET
    submission_id: str | Unset = ""
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        book_id = self.book_id

        page_id = self.page_id

        block_id = self.block_id

        question_id = self.question_id

        user_answer = self.user_answer

        is_correct: bool | None | Unset
        if isinstance(self.is_correct, Unset):
            is_correct = UNSET
        else:
            is_correct = self.is_correct

        submission_id = self.submission_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "book_id": book_id,
                "page_id": page_id,
                "block_id": block_id,
            }
        )
        if question_id is not UNSET:
            field_dict["question_id"] = question_id
        if user_answer is not UNSET:
            field_dict["user_answer"] = user_answer
        if is_correct is not UNSET:
            field_dict["is_correct"] = is_correct
        if submission_id is not UNSET:
            field_dict["submission_id"] = submission_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        book_id = d.pop("book_id")

        page_id = d.pop("page_id")

        block_id = d.pop("block_id")

        question_id = d.pop("question_id", UNSET)

        user_answer = d.pop("user_answer", UNSET)

        def _parse_is_correct(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        is_correct = _parse_is_correct(d.pop("is_correct", UNSET))

        submission_id = d.pop("submission_id", UNSET)

        quiz_attempt_request = cls(
            book_id=book_id,
            page_id=page_id,
            block_id=block_id,
            question_id=question_id,
            user_answer=user_answer,
            is_correct=is_correct,
            submission_id=submission_id,
        )

        quiz_attempt_request.additional_properties = d
        return quiz_attempt_request

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
