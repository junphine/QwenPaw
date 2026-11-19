from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Literal, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.turn import Turn


T = TypeVar("T", bound="SubmissionReplacementResponse")


@_attrs_define
class SubmissionReplacementResponse:
    """
    Attributes:
        status (Literal['started']):
        session_id (str):
        submission_id (str):
        turn (Turn):
    """

    status: Literal["started"]
    session_id: str
    submission_id: str
    turn: Turn
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        status = self.status

        session_id = self.session_id

        submission_id = self.submission_id

        turn = self.turn.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "status": status,
                "session_id": session_id,
                "submission_id": submission_id,
                "turn": turn,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.turn import Turn  # noqa: PLC0415

        d = dict(src_dict)
        status = cast(Literal["started"], d.pop("status"))
        if status != "started":
            raise ValueError(f"status must match const 'started', got '{status}'")

        session_id = d.pop("session_id")

        submission_id = d.pop("submission_id")

        turn = Turn.from_dict(d.pop("turn"))

        submission_replacement_response = cls(
            status=status,
            session_id=session_id,
            submission_id=submission_id,
            turn=turn,
        )

        submission_replacement_response.additional_properties = d
        return submission_replacement_response

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
