from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="LinkTasks")


@_attrs_define
class LinkTasks:
    """
    Attributes:
        task_ids (list[str]):
        workspace_id (str | Unset):  Default: ''.
    """

    task_ids: list[str]
    workspace_id: str | Unset = ""

    def to_dict(self) -> dict[str, Any]:
        task_ids = self.task_ids

        workspace_id = self.workspace_id

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "task_ids": task_ids,
            }
        )
        if workspace_id is not UNSET:
            field_dict["workspace_id"] = workspace_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        task_ids = cast(list[str], d.pop("task_ids"))

        workspace_id = d.pop("workspace_id", UNSET)

        link_tasks = cls(
            task_ids=task_ids,
            workspace_id=workspace_id,
        )

        return link_tasks
