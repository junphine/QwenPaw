from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="SessionTaskLinks")


@_attrs_define
class SessionTaskLinks:
    """
    Attributes:
        workspace_id (str):
        session_id (str):
        task_ids (list[str] | Unset):
        status_link_enabled (bool | Unset):  Default: True.
    """

    workspace_id: str
    session_id: str
    task_ids: list[str] | Unset = UNSET
    status_link_enabled: bool | Unset = True
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        workspace_id = self.workspace_id

        session_id = self.session_id

        task_ids: list[str] | Unset = UNSET
        if not isinstance(self.task_ids, Unset):
            task_ids = self.task_ids

        status_link_enabled = self.status_link_enabled

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "workspace_id": workspace_id,
                "session_id": session_id,
            }
        )
        if task_ids is not UNSET:
            field_dict["task_ids"] = task_ids
        if status_link_enabled is not UNSET:
            field_dict["status_link_enabled"] = status_link_enabled

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        workspace_id = d.pop("workspace_id")

        session_id = d.pop("session_id")

        task_ids = cast(list[str], d.pop("task_ids", UNSET))

        status_link_enabled = d.pop("status_link_enabled", UNSET)

        session_task_links = cls(
            workspace_id=workspace_id,
            session_id=session_id,
            task_ids=task_ids,
            status_link_enabled=status_link_enabled,
        )

        session_task_links.additional_properties = d
        return session_task_links

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
