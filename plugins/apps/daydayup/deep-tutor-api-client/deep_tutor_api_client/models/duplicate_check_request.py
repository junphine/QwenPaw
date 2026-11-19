from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.duplicate_file_query import DuplicateFileQuery


T = TypeVar("T", bound="DuplicateCheckRequest")


@_attrs_define
class DuplicateCheckRequest:
    """
    Attributes:
        files (list[DuplicateFileQuery] | Unset):
        urls (list[str] | Unset):
    """

    files: list[DuplicateFileQuery] | Unset = UNSET
    urls: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        files: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.files, Unset):
            files = []
            for files_item_data in self.files:
                files_item = files_item_data.to_dict()
                files.append(files_item)

        urls: list[str] | Unset = UNSET
        if not isinstance(self.urls, Unset):
            urls = self.urls

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if files is not UNSET:
            field_dict["files"] = files
        if urls is not UNSET:
            field_dict["urls"] = urls

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.duplicate_file_query import DuplicateFileQuery  # noqa: PLC0415

        d = dict(src_dict)
        _files = d.pop("files", UNSET)
        files: list[DuplicateFileQuery] | Unset = UNSET
        if _files is not UNSET:
            files = []
            for files_item_data in _files:
                files_item = DuplicateFileQuery.from_dict(files_item_data)

                files.append(files_item)

        urls = cast(list[str], d.pop("urls", UNSET))

        duplicate_check_request = cls(
            files=files,
            urls=urls,
        )

        duplicate_check_request.additional_properties = d
        return duplicate_check_request

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
