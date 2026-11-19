from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GitHubSourceInfo")


@_attrs_define
class GitHubSourceInfo:
    """
    Attributes:
        id (str):
        repo (str):
        branch (str):
        path (str):
        glob (str):
        enabled (bool | Unset):  Default: True.
        last_synced_sha (str | Unset):  Default: ''.
        last_synced_at (str | Unset):  Default: ''.
        last_sync_status (str | Unset):  Default: 'pending'.
        last_sync_error (None | str | Unset):
        files_synced (int | Unset):  Default: 0.
        added_at (str | Unset):  Default: ''.
    """

    id: str
    repo: str
    branch: str
    path: str
    glob: str
    enabled: bool | Unset = True
    last_synced_sha: str | Unset = ""
    last_synced_at: str | Unset = ""
    last_sync_status: str | Unset = "pending"
    last_sync_error: None | str | Unset = UNSET
    files_synced: int | Unset = 0
    added_at: str | Unset = ""
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        repo = self.repo

        branch = self.branch

        path = self.path

        glob = self.glob

        enabled = self.enabled

        last_synced_sha = self.last_synced_sha

        last_synced_at = self.last_synced_at

        last_sync_status = self.last_sync_status

        last_sync_error: None | str | Unset
        if isinstance(self.last_sync_error, Unset):
            last_sync_error = UNSET
        else:
            last_sync_error = self.last_sync_error

        files_synced = self.files_synced

        added_at = self.added_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "repo": repo,
                "branch": branch,
                "path": path,
                "glob": glob,
            }
        )
        if enabled is not UNSET:
            field_dict["enabled"] = enabled
        if last_synced_sha is not UNSET:
            field_dict["last_synced_sha"] = last_synced_sha
        if last_synced_at is not UNSET:
            field_dict["last_synced_at"] = last_synced_at
        if last_sync_status is not UNSET:
            field_dict["last_sync_status"] = last_sync_status
        if last_sync_error is not UNSET:
            field_dict["last_sync_error"] = last_sync_error
        if files_synced is not UNSET:
            field_dict["files_synced"] = files_synced
        if added_at is not UNSET:
            field_dict["added_at"] = added_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        repo = d.pop("repo")

        branch = d.pop("branch")

        path = d.pop("path")

        glob = d.pop("glob")

        enabled = d.pop("enabled", UNSET)

        last_synced_sha = d.pop("last_synced_sha", UNSET)

        last_synced_at = d.pop("last_synced_at", UNSET)

        last_sync_status = d.pop("last_sync_status", UNSET)

        def _parse_last_sync_error(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        last_sync_error = _parse_last_sync_error(d.pop("last_sync_error", UNSET))

        files_synced = d.pop("files_synced", UNSET)

        added_at = d.pop("added_at", UNSET)

        git_hub_source_info = cls(
            id=id,
            repo=repo,
            branch=branch,
            path=path,
            glob=glob,
            enabled=enabled,
            last_synced_sha=last_synced_sha,
            last_synced_at=last_synced_at,
            last_sync_status=last_sync_status,
            last_sync_error=last_sync_error,
            files_synced=files_synced,
            added_at=added_at,
        )

        git_hub_source_info.additional_properties = d
        return git_hub_source_info

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
