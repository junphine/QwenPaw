from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.mastery_card_answer_answers_type_0 import MasteryCardAnswerAnswersType0


T = TypeVar("T", bound="MasteryCardAnswer")


@_attrs_define
class MasteryCardAnswer:
    """An answer submitted from a mastery question card.

    The card outlives the turn that posed it — posing a question ends that
    turn — so the answer arrives as the next turn's message. This says which
    question the message is answering, letting the runtime commit it to the
    engine before the tutor's first token instead of asking the model to
    recover the pairing from prose.

        Attributes:
            question_id (str):
            text (str):
            answers (MasteryCardAnswerAnswersType0 | None | Unset):
    """

    question_id: str
    text: str
    answers: MasteryCardAnswerAnswersType0 | None | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        from ..models.mastery_card_answer_answers_type_0 import MasteryCardAnswerAnswersType0  # noqa: PLC0415

        question_id = self.question_id

        text = self.text

        answers: dict[str, Any] | None | Unset
        if isinstance(self.answers, Unset):
            answers = UNSET
        elif isinstance(self.answers, MasteryCardAnswerAnswersType0):
            answers = self.answers.to_dict()
        else:
            answers = self.answers

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "question_id": question_id,
                "text": text,
            }
        )
        if answers is not UNSET:
            field_dict["answers"] = answers

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.mastery_card_answer_answers_type_0 import MasteryCardAnswerAnswersType0  # noqa: PLC0415

        d = dict(src_dict)
        question_id = d.pop("question_id")

        text = d.pop("text")

        def _parse_answers(data: object) -> MasteryCardAnswerAnswersType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                answers_type_0 = MasteryCardAnswerAnswersType0.from_dict(data)

                return answers_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(MasteryCardAnswerAnswersType0 | None | Unset, data)

        answers = _parse_answers(d.pop("answers", UNSET))

        mastery_card_answer = cls(
            question_id=question_id,
            text=text,
            answers=answers,
        )

        return mastery_card_answer
