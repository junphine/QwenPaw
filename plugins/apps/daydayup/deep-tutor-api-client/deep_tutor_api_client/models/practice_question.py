from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.notebook_entry_item import NotebookEntryItem
    from ..models.state import State


T = TypeVar("T", bound="PracticeQuestion")


@_attrs_define
class PracticeQuestion:
    """
    Attributes:
        entry (NotebookEntryItem):
        state (State):
        content_workspace_id (str | Unset):  Default: ''.
        content_workspace_name (str | Unset):  Default: ''.
    """

    entry: NotebookEntryItem
    state: State
    content_workspace_id: str | Unset = ""
    content_workspace_name: str | Unset = ""
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        entry = self.entry.to_dict()

        state = self.state.to_dict()

        content_workspace_id = self.content_workspace_id

        content_workspace_name = self.content_workspace_name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "entry": entry,
                "state": state,
            }
        )
        if content_workspace_id is not UNSET:
            field_dict["content_workspace_id"] = content_workspace_id
        if content_workspace_name is not UNSET:
            field_dict["content_workspace_name"] = content_workspace_name

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.notebook_entry_item import NotebookEntryItem  # noqa: PLC0415
        from ..models.state import State  # noqa: PLC0415

        d = dict(src_dict)
        entry = NotebookEntryItem.from_dict(d.pop("entry"))

        state = State.from_dict(d.pop("state"))

        content_workspace_id = d.pop("content_workspace_id", UNSET)

        content_workspace_name = d.pop("content_workspace_name", UNSET)

        practice_question = cls(
            entry=entry,
            state=state,
            content_workspace_id=content_workspace_id,
            content_workspace_name=content_workspace_name,
        )

        practice_question.additional_properties = d
        return practice_question

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
