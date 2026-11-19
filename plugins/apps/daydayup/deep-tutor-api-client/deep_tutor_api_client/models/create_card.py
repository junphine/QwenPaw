from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateCard")


@_attrs_define
class CreateCard:
    """
    Attributes:
        title (str):
        note (str | Unset):  Default: ''.
        due_date (None | str | Unset):
    """

    title: str
    note: str | Unset = ""
    due_date: None | str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        title = self.title

        note = self.note

        due_date: None | str | Unset
        if isinstance(self.due_date, Unset):
            due_date = UNSET
        else:
            due_date = self.due_date

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "title": title,
            }
        )
        if note is not UNSET:
            field_dict["note"] = note
        if due_date is not UNSET:
            field_dict["due_date"] = due_date

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        title = d.pop("title")

        note = d.pop("note", UNSET)

        def _parse_due_date(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        due_date = _parse_due_date(d.pop("due_date", UNSET))

        create_card = cls(
            title=title,
            note=note,
            due_date=due_date,
        )

        return create_card
