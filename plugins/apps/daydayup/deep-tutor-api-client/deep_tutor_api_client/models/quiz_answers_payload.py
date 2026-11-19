from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.quiz_answer_item import QuizAnswerItem


T = TypeVar("T", bound="QuizAnswersPayload")


@_attrs_define
class QuizAnswersPayload:
    """
    Attributes:
        locator (int):
        answers (list[QuizAnswerItem]):
        source_anchor (str | Unset):  Default: ''.
        section_title (str | Unset):  Default: ''.
        session_id (str | Unset):  Default: ''.
        turn_id (str | Unset):  Default: ''.
        submission_id (str | Unset):  Default: ''.
    """

    locator: int
    answers: list[QuizAnswerItem]
    source_anchor: str | Unset = ""
    section_title: str | Unset = ""
    session_id: str | Unset = ""
    turn_id: str | Unset = ""
    submission_id: str | Unset = ""
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        locator = self.locator

        answers = []
        for answers_item_data in self.answers:
            answers_item = answers_item_data.to_dict()
            answers.append(answers_item)

        source_anchor = self.source_anchor

        section_title = self.section_title

        session_id = self.session_id

        turn_id = self.turn_id

        submission_id = self.submission_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "locator": locator,
                "answers": answers,
            }
        )
        if source_anchor is not UNSET:
            field_dict["source_anchor"] = source_anchor
        if section_title is not UNSET:
            field_dict["section_title"] = section_title
        if session_id is not UNSET:
            field_dict["session_id"] = session_id
        if turn_id is not UNSET:
            field_dict["turn_id"] = turn_id
        if submission_id is not UNSET:
            field_dict["submission_id"] = submission_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.quiz_answer_item import QuizAnswerItem  # noqa: PLC0415

        d = dict(src_dict)
        locator = d.pop("locator")

        answers = []
        _answers = d.pop("answers")
        for answers_item_data in _answers:
            answers_item = QuizAnswerItem.from_dict(answers_item_data)

            answers.append(answers_item)

        source_anchor = d.pop("source_anchor", UNSET)

        section_title = d.pop("section_title", UNSET)

        session_id = d.pop("session_id", UNSET)

        turn_id = d.pop("turn_id", UNSET)

        submission_id = d.pop("submission_id", UNSET)

        quiz_answers_payload = cls(
            locator=locator,
            answers=answers,
            source_anchor=source_anchor,
            section_title=section_title,
            session_id=session_id,
            turn_id=turn_id,
            submission_id=submission_id,
        )

        quiz_answers_payload.additional_properties = d
        return quiz_answers_payload

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
