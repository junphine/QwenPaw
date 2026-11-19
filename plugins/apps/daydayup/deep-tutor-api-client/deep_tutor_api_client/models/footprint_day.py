from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.footprint_session import FootprintSession


T = TypeVar("T", bound="FootprintDay")


@_attrs_define
class FootprintDay:
    """
    Attributes:
        date (str):
        session_count (int | Unset):  Default: 0.
        sessions (list[FootprintSession] | Unset):
        practice_reviews (int | Unset):  Default: 0.
        mastery_evidence (int | Unset):  Default: 0.
    """

    date: str
    session_count: int | Unset = 0
    sessions: list[FootprintSession] | Unset = UNSET
    practice_reviews: int | Unset = 0
    mastery_evidence: int | Unset = 0
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        date = self.date

        session_count = self.session_count

        sessions: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.sessions, Unset):
            sessions = []
            for sessions_item_data in self.sessions:
                sessions_item = sessions_item_data.to_dict()
                sessions.append(sessions_item)

        practice_reviews = self.practice_reviews

        mastery_evidence = self.mastery_evidence

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "date": date,
            }
        )
        if session_count is not UNSET:
            field_dict["session_count"] = session_count
        if sessions is not UNSET:
            field_dict["sessions"] = sessions
        if practice_reviews is not UNSET:
            field_dict["practice_reviews"] = practice_reviews
        if mastery_evidence is not UNSET:
            field_dict["mastery_evidence"] = mastery_evidence

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.footprint_session import FootprintSession  # noqa: PLC0415

        d = dict(src_dict)
        date = d.pop("date")

        session_count = d.pop("session_count", UNSET)

        _sessions = d.pop("sessions", UNSET)
        sessions: list[FootprintSession] | Unset = UNSET
        if _sessions is not UNSET:
            sessions = []
            for sessions_item_data in _sessions:
                sessions_item = FootprintSession.from_dict(sessions_item_data)

                sessions.append(sessions_item)

        practice_reviews = d.pop("practice_reviews", UNSET)

        mastery_evidence = d.pop("mastery_evidence", UNSET)

        footprint_day = cls(
            date=date,
            session_count=session_count,
            sessions=sessions,
            practice_reviews=practice_reviews,
            mastery_evidence=mastery_evidence,
        )

        footprint_day.additional_properties = d
        return footprint_day

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
