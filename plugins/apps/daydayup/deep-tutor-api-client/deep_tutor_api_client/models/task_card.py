from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ..models.task_card_status import TaskCardStatus, check_task_card_status
from ..types import UNSET, Unset

T = TypeVar("T", bound="TaskCard")


@_attrs_define
class TaskCard:
    """
    Attributes:
        title (str):
        id (str):
        status (TaskCardStatus):
        archived (bool):
        created_at (str):
        updated_at (str):
        note (str | Unset):  Default: ''.
        due_date (None | str | Unset):
        workspace_id (None | str | Unset):
    """

    title: str
    id: str
    status: TaskCardStatus
    archived: bool
    created_at: str
    updated_at: str
    note: str | Unset = ""
    due_date: None | str | Unset = UNSET
    workspace_id: None | str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        title = self.title

        id = self.id

        status: str = self.status

        archived = self.archived

        created_at = self.created_at

        updated_at = self.updated_at

        note = self.note

        due_date: None | str | Unset
        if isinstance(self.due_date, Unset):
            due_date = UNSET
        else:
            due_date = self.due_date

        workspace_id: None | str | Unset
        if isinstance(self.workspace_id, Unset):
            workspace_id = UNSET
        else:
            workspace_id = self.workspace_id

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "title": title,
                "id": id,
                "status": status,
                "archived": archived,
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )
        if note is not UNSET:
            field_dict["note"] = note
        if due_date is not UNSET:
            field_dict["due_date"] = due_date
        if workspace_id is not UNSET:
            field_dict["workspace_id"] = workspace_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        title = d.pop("title")

        id = d.pop("id")

        status = check_task_card_status(d.pop("status"))

        archived = d.pop("archived")

        created_at = d.pop("created_at")

        updated_at = d.pop("updated_at")

        note = d.pop("note", UNSET)

        def _parse_due_date(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        due_date = _parse_due_date(d.pop("due_date", UNSET))

        def _parse_workspace_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        workspace_id = _parse_workspace_id(d.pop("workspace_id", UNSET))

        task_card = cls(
            title=title,
            id=id,
            status=status,
            archived=archived,
            created_at=created_at,
            updated_at=updated_at,
            note=note,
            due_date=due_date,
            workspace_id=workspace_id,
        )

        return task_card
