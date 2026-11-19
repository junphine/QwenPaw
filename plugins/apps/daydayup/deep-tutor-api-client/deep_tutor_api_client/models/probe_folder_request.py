from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ProbeFolderRequest")


@_attrs_define
class ProbeFolderRequest:
    """
    Attributes:
        folder_path (str):
        rag_provider (str | Unset):  Default: 'llamaindex'.
    """

    folder_path: str
    rag_provider: str | Unset = "llamaindex"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        folder_path = self.folder_path

        rag_provider = self.rag_provider

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "folder_path": folder_path,
            }
        )
        if rag_provider is not UNSET:
            field_dict["rag_provider"] = rag_provider

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        folder_path = d.pop("folder_path")

        rag_provider = d.pop("rag_provider", UNSET)

        probe_folder_request = cls(
            folder_path=folder_path,
            rag_provider=rag_provider,
        )

        probe_folder_request.additional_properties = d
        return probe_folder_request

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
