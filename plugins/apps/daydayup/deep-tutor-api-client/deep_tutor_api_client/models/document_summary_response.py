from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="DocumentSummaryResponse")


@_attrs_define
class DocumentSummaryResponse:
    """
    Attributes:
        id (str):
        title (str):
        created_at (float):
        updated_at (float):
        preview (str | Unset):  Default: ''.
        parent_id (None | str | Unset):
        icon (str | Unset):  Default: ''.
        cover (str | Unset):  Default: ''.
        pinned (bool | Unset):  Default: False.
        revision (int | Unset):  Default: 0.
    """

    id: str
    title: str
    created_at: float
    updated_at: float
    preview: str | Unset = ""
    parent_id: None | str | Unset = UNSET
    icon: str | Unset = ""
    cover: str | Unset = ""
    pinned: bool | Unset = False
    revision: int | Unset = 0
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        title = self.title

        created_at = self.created_at

        updated_at = self.updated_at

        preview = self.preview

        parent_id: None | str | Unset
        if isinstance(self.parent_id, Unset):
            parent_id = UNSET
        else:
            parent_id = self.parent_id

        icon = self.icon

        cover = self.cover

        pinned = self.pinned

        revision = self.revision

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "title": title,
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )
        if preview is not UNSET:
            field_dict["preview"] = preview
        if parent_id is not UNSET:
            field_dict["parent_id"] = parent_id
        if icon is not UNSET:
            field_dict["icon"] = icon
        if cover is not UNSET:
            field_dict["cover"] = cover
        if pinned is not UNSET:
            field_dict["pinned"] = pinned
        if revision is not UNSET:
            field_dict["revision"] = revision

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        title = d.pop("title")

        created_at = d.pop("created_at")

        updated_at = d.pop("updated_at")

        preview = d.pop("preview", UNSET)

        def _parse_parent_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        parent_id = _parse_parent_id(d.pop("parent_id", UNSET))

        icon = d.pop("icon", UNSET)

        cover = d.pop("cover", UNSET)

        pinned = d.pop("pinned", UNSET)

        revision = d.pop("revision", UNSET)

        document_summary_response = cls(
            id=id,
            title=title,
            created_at=created_at,
            updated_at=updated_at,
            preview=preview,
            parent_id=parent_id,
            icon=icon,
            cover=cover,
            pinned=pinned,
            revision=revision,
        )

        document_summary_response.additional_properties = d
        return document_summary_response

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
