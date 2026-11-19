from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="UrlImportRequest")


@_attrs_define
class UrlImportRequest:
    """
    Attributes:
        urls (list[str]):
        workspace_id (str | Unset):  Default: ''.
        workspace_title (str | Unset):  Default: ''.
    """

    urls: list[str]
    workspace_id: str | Unset = ""
    workspace_title: str | Unset = ""
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        urls = self.urls

        workspace_id = self.workspace_id

        workspace_title = self.workspace_title

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "urls": urls,
            }
        )
        if workspace_id is not UNSET:
            field_dict["workspace_id"] = workspace_id
        if workspace_title is not UNSET:
            field_dict["workspace_title"] = workspace_title

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        urls = cast(list[str], d.pop("urls"))

        workspace_id = d.pop("workspace_id", UNSET)

        workspace_title = d.pop("workspace_title", UNSET)

        url_import_request = cls(
            urls=urls,
            workspace_id=workspace_id,
            workspace_title=workspace_title,
        )

        url_import_request.additional_properties = d
        return url_import_request

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
