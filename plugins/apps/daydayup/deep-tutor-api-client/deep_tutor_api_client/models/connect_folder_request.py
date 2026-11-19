from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ConnectFolderRequest")


@_attrs_define
class ConnectFolderRequest:
    """
    Attributes:
        name (str):
        folder_path (str):
        description (str | Unset):  Default: ''.
        rag_provider (str | Unset):  Default: 'llamaindex'.
    """

    name: str
    folder_path: str
    description: str | Unset = ""
    rag_provider: str | Unset = "llamaindex"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        folder_path = self.folder_path

        description = self.description

        rag_provider = self.rag_provider

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "folder_path": folder_path,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if rag_provider is not UNSET:
            field_dict["rag_provider"] = rag_provider

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        folder_path = d.pop("folder_path")

        description = d.pop("description", UNSET)

        rag_provider = d.pop("rag_provider", UNSET)

        connect_folder_request = cls(
            name=name,
            folder_path=folder_path,
            description=description,
            rag_provider=rag_provider,
        )

        connect_folder_request.additional_properties = d
        return connect_folder_request

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
