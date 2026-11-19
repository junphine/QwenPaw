from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.selected_branches import SelectedBranches


T = TypeVar("T", bound="BranchSelectionRequest")


@_attrs_define
class BranchSelectionRequest:
    """Edit-branch picker state: `{parent_message_id: chosen_child_id}`.

    Stored inside the session preferences blob so it survives reloads
    without a dedicated column.

        Attributes:
            selected_branches (SelectedBranches | Unset):
    """

    selected_branches: SelectedBranches | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        selected_branches: dict[str, Any] | Unset = UNSET
        if not isinstance(self.selected_branches, Unset):
            selected_branches = self.selected_branches.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if selected_branches is not UNSET:
            field_dict["selected_branches"] = selected_branches

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.selected_branches import SelectedBranches  # noqa: PLC0415

        d = dict(src_dict)
        _selected_branches = d.pop("selected_branches", UNSET)
        selected_branches: SelectedBranches | Unset
        if isinstance(_selected_branches, Unset):
            selected_branches = UNSET
        else:
            selected_branches = SelectedBranches.from_dict(_selected_branches)

        branch_selection_request = cls(
            selected_branches=selected_branches,
        )

        branch_selection_request.additional_properties = d
        return branch_selection_request

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
