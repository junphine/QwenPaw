from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ..models.update_card_status_type_0 import UpdateCardStatusType0, check_update_card_status_type_0
from ..types import UNSET, Unset

T = TypeVar("T", bound="UpdateCard")


@_attrs_define
class UpdateCard:
    """
    Attributes:
        title (None | str | Unset):
        note (None | str | Unset):
        status (None | Unset | UpdateCardStatusType0):
        archived (bool | None | Unset):
        workspace_id (None | str | Unset):
        due_date (None | str | Unset):
    """

    title: None | str | Unset = UNSET
    note: None | str | Unset = UNSET
    status: None | Unset | UpdateCardStatusType0 = UNSET
    archived: bool | None | Unset = UNSET
    workspace_id: None | str | Unset = UNSET
    due_date: None | str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        title: None | str | Unset
        if isinstance(self.title, Unset):
            title = UNSET
        else:
            title = self.title

        note: None | str | Unset
        if isinstance(self.note, Unset):
            note = UNSET
        else:
            note = self.note

        status: None | str | Unset
        if isinstance(self.status, Unset):
            status = UNSET
        elif isinstance(self.status, str):
            status = self.status
        else:
            status = self.status

        archived: bool | None | Unset
        if isinstance(self.archived, Unset):
            archived = UNSET
        else:
            archived = self.archived

        workspace_id: None | str | Unset
        if isinstance(self.workspace_id, Unset):
            workspace_id = UNSET
        else:
            workspace_id = self.workspace_id

        due_date: None | str | Unset
        if isinstance(self.due_date, Unset):
            due_date = UNSET
        else:
            due_date = self.due_date

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if title is not UNSET:
            field_dict["title"] = title
        if note is not UNSET:
            field_dict["note"] = note
        if status is not UNSET:
            field_dict["status"] = status
        if archived is not UNSET:
            field_dict["archived"] = archived
        if workspace_id is not UNSET:
            field_dict["workspace_id"] = workspace_id
        if due_date is not UNSET:
            field_dict["due_date"] = due_date

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_title(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        title = _parse_title(d.pop("title", UNSET))

        def _parse_note(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        note = _parse_note(d.pop("note", UNSET))

        def _parse_status(data: object) -> None | Unset | UpdateCardStatusType0:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                status_type_0 = check_update_card_status_type_0(data)

                return status_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UpdateCardStatusType0, data)

        status = _parse_status(d.pop("status", UNSET))

        def _parse_archived(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        archived = _parse_archived(d.pop("archived", UNSET))

        def _parse_workspace_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        workspace_id = _parse_workspace_id(d.pop("workspace_id", UNSET))

        def _parse_due_date(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        due_date = _parse_due_date(d.pop("due_date", UNSET))

        update_card = cls(
            title=title,
            note=note,
            status=status,
            archived=archived,
            workspace_id=workspace_id,
            due_date=due_date,
        )

        return update_card
