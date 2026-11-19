from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="MasteryCardSkip")


@_attrs_define
class MasteryCardSkip:
    """A question the learner dropped instead of answering.

    The same shape of problem as :class:`MasteryCardAnswer`: the card outlives
    the turn that posed it, so "not this one" also arrives as the next turn's
    message. Naming the question is what keeps the runtime from abandoning
    whatever happens to be open by the time the turn starts.

        Attributes:
            question_id (str):
    """

    question_id: str

    def to_dict(self) -> dict[str, Any]:
        question_id = self.question_id

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "question_id": question_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        question_id = d.pop("question_id")

        mastery_card_skip = cls(
            question_id=question_id,
        )

        return mastery_card_skip
