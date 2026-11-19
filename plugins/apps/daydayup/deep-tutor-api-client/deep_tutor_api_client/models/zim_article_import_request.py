from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ZimArticleImportRequest")


@_attrs_define
class ZimArticleImportRequest:
    """
    Attributes:
        kb_ref (str):
        article_path (str):
        title (str | Unset):  Default: ''.
        workspace_id (str | Unset):  Default: ''.
    """

    kb_ref: str
    article_path: str
    title: str | Unset = ""
    workspace_id: str | Unset = ""
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        kb_ref = self.kb_ref

        article_path = self.article_path

        title = self.title

        workspace_id = self.workspace_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "kb_ref": kb_ref,
                "article_path": article_path,
            }
        )
        if title is not UNSET:
            field_dict["title"] = title
        if workspace_id is not UNSET:
            field_dict["workspace_id"] = workspace_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        kb_ref = d.pop("kb_ref")

        article_path = d.pop("article_path")

        title = d.pop("title", UNSET)

        workspace_id = d.pop("workspace_id", UNSET)

        zim_article_import_request = cls(
            kb_ref=kb_ref,
            article_path=article_path,
            title=title,
            workspace_id=workspace_id,
        )

        zim_article_import_request.additional_properties = d
        return zim_article_import_request

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
