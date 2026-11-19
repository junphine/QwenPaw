from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="AddGitHubSourceRequest")


@_attrs_define
class AddGitHubSourceRequest:
    """
    Attributes:
        repo (str):
        branch (str | Unset):  Default: 'main'.
        path (str | Unset):  Default: ''.
        glob (str | Unset):  Default: '*.md'.
    """

    repo: str
    branch: str | Unset = "main"
    path: str | Unset = ""
    glob: str | Unset = "*.md"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        repo = self.repo

        branch = self.branch

        path = self.path

        glob = self.glob

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "repo": repo,
            }
        )
        if branch is not UNSET:
            field_dict["branch"] = branch
        if path is not UNSET:
            field_dict["path"] = path
        if glob is not UNSET:
            field_dict["glob"] = glob

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        repo = d.pop("repo")

        branch = d.pop("branch", UNSET)

        path = d.pop("path", UNSET)

        glob = d.pop("glob", UNSET)

        add_git_hub_source_request = cls(
            repo=repo,
            branch=branch,
            path=path,
            glob=glob,
        )

        add_git_hub_source_request.additional_properties = d
        return add_git_hub_source_request

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
