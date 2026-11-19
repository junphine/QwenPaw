from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="SyncFolderResponse")


@_attrs_define
class SyncFolderResponse:
    """Response model for a linked-folder sync request.

    Attributes:
        message (str):
        files (list[str]):
        new_files (int):
        modified_files (int):
        file_count (int):
        task_id (None | str):
        folder_path (None | str | Unset):
    """

    message: str
    files: list[str]
    new_files: int
    modified_files: int
    file_count: int
    task_id: None | str
    folder_path: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        message = self.message

        files = self.files

        new_files = self.new_files

        modified_files = self.modified_files

        file_count = self.file_count

        task_id: None | str
        task_id = self.task_id

        folder_path: None | str | Unset
        if isinstance(self.folder_path, Unset):
            folder_path = UNSET
        else:
            folder_path = self.folder_path

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "message": message,
                "files": files,
                "new_files": new_files,
                "modified_files": modified_files,
                "file_count": file_count,
                "task_id": task_id,
            }
        )
        if folder_path is not UNSET:
            field_dict["folder_path"] = folder_path

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        message = d.pop("message")

        files = cast(list[str], d.pop("files"))

        new_files = d.pop("new_files")

        modified_files = d.pop("modified_files")

        file_count = d.pop("file_count")

        def _parse_task_id(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        task_id = _parse_task_id(d.pop("task_id"))

        def _parse_folder_path(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        folder_path = _parse_folder_path(d.pop("folder_path", UNSET))

        sync_folder_response = cls(
            message=message,
            files=files,
            new_files=new_files,
            modified_files=modified_files,
            file_count=file_count,
            task_id=task_id,
            folder_path=folder_path,
        )

        sync_folder_response.additional_properties = d
        return sync_folder_response

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
