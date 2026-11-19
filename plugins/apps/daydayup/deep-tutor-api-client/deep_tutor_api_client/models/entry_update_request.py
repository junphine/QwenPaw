from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="EntryUpdateRequest")


@_attrs_define
class EntryUpdateRequest:
    """
    Attributes:
        bookmarked (bool | None | Unset):
        followup_session_id (None | str | Unset):
        ai_judgment (None | str | Unset):
        resolved (bool | None | Unset):
    """

    bookmarked: bool | None | Unset = UNSET
    followup_session_id: None | str | Unset = UNSET
    ai_judgment: None | str | Unset = UNSET
    resolved: bool | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        bookmarked: bool | None | Unset
        if isinstance(self.bookmarked, Unset):
            bookmarked = UNSET
        else:
            bookmarked = self.bookmarked

        followup_session_id: None | str | Unset
        if isinstance(self.followup_session_id, Unset):
            followup_session_id = UNSET
        else:
            followup_session_id = self.followup_session_id

        ai_judgment: None | str | Unset
        if isinstance(self.ai_judgment, Unset):
            ai_judgment = UNSET
        else:
            ai_judgment = self.ai_judgment

        resolved: bool | None | Unset
        if isinstance(self.resolved, Unset):
            resolved = UNSET
        else:
            resolved = self.resolved

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if bookmarked is not UNSET:
            field_dict["bookmarked"] = bookmarked
        if followup_session_id is not UNSET:
            field_dict["followup_session_id"] = followup_session_id
        if ai_judgment is not UNSET:
            field_dict["ai_judgment"] = ai_judgment
        if resolved is not UNSET:
            field_dict["resolved"] = resolved

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_bookmarked(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        bookmarked = _parse_bookmarked(d.pop("bookmarked", UNSET))

        def _parse_followup_session_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        followup_session_id = _parse_followup_session_id(d.pop("followup_session_id", UNSET))

        def _parse_ai_judgment(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        ai_judgment = _parse_ai_judgment(d.pop("ai_judgment", UNSET))

        def _parse_resolved(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        resolved = _parse_resolved(d.pop("resolved", UNSET))

        entry_update_request = cls(
            bookmarked=bookmarked,
            followup_session_id=followup_session_id,
            ai_judgment=ai_judgment,
            resolved=resolved,
        )

        entry_update_request.additional_properties = d
        return entry_update_request

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
