from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.raw import Raw


T = TypeVar("T", bound="SyncObjectIn")


@_attrs_define
class SyncObjectIn:
    """
    Attributes:
        object_id (str):
        object_type (str):
        title (str | Unset):  Default: ''.
        content (str | Unset):  Default: ''.
        excerpt (None | str | Unset):
        document_id (None | str | Unset):
        document_title (None | str | Unset):
        page (int | None | Unset):
        tags (list[str] | Unset):
        links (list[str] | Unset):
        color (None | str | Unset):
        created_at (str | Unset):  Default: ''.
        updated_at (str | Unset):  Default: ''.
        raw (Raw | Unset):
    """

    object_id: str
    object_type: str
    title: str | Unset = ""
    content: str | Unset = ""
    excerpt: None | str | Unset = UNSET
    document_id: None | str | Unset = UNSET
    document_title: None | str | Unset = UNSET
    page: int | None | Unset = UNSET
    tags: list[str] | Unset = UNSET
    links: list[str] | Unset = UNSET
    color: None | str | Unset = UNSET
    created_at: str | Unset = ""
    updated_at: str | Unset = ""
    raw: Raw | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        object_id = self.object_id

        object_type = self.object_type

        title = self.title

        content = self.content

        excerpt: None | str | Unset
        if isinstance(self.excerpt, Unset):
            excerpt = UNSET
        else:
            excerpt = self.excerpt

        document_id: None | str | Unset
        if isinstance(self.document_id, Unset):
            document_id = UNSET
        else:
            document_id = self.document_id

        document_title: None | str | Unset
        if isinstance(self.document_title, Unset):
            document_title = UNSET
        else:
            document_title = self.document_title

        page: int | None | Unset
        if isinstance(self.page, Unset):
            page = UNSET
        else:
            page = self.page

        tags: list[str] | Unset = UNSET
        if not isinstance(self.tags, Unset):
            tags = self.tags

        links: list[str] | Unset = UNSET
        if not isinstance(self.links, Unset):
            links = self.links

        color: None | str | Unset
        if isinstance(self.color, Unset):
            color = UNSET
        else:
            color = self.color

        created_at = self.created_at

        updated_at = self.updated_at

        raw: dict[str, Any] | Unset = UNSET
        if not isinstance(self.raw, Unset):
            raw = self.raw.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "object_id": object_id,
                "object_type": object_type,
            }
        )
        if title is not UNSET:
            field_dict["title"] = title
        if content is not UNSET:
            field_dict["content"] = content
        if excerpt is not UNSET:
            field_dict["excerpt"] = excerpt
        if document_id is not UNSET:
            field_dict["document_id"] = document_id
        if document_title is not UNSET:
            field_dict["document_title"] = document_title
        if page is not UNSET:
            field_dict["page"] = page
        if tags is not UNSET:
            field_dict["tags"] = tags
        if links is not UNSET:
            field_dict["links"] = links
        if color is not UNSET:
            field_dict["color"] = color
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at
        if raw is not UNSET:
            field_dict["raw"] = raw

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.raw import Raw  # noqa: PLC0415

        d = dict(src_dict)
        object_id = d.pop("object_id")

        object_type = d.pop("object_type")

        title = d.pop("title", UNSET)

        content = d.pop("content", UNSET)

        def _parse_excerpt(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        excerpt = _parse_excerpt(d.pop("excerpt", UNSET))

        def _parse_document_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        document_id = _parse_document_id(d.pop("document_id", UNSET))

        def _parse_document_title(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        document_title = _parse_document_title(d.pop("document_title", UNSET))

        def _parse_page(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        page = _parse_page(d.pop("page", UNSET))

        tags = cast(list[str], d.pop("tags", UNSET))

        links = cast(list[str], d.pop("links", UNSET))

        def _parse_color(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        color = _parse_color(d.pop("color", UNSET))

        created_at = d.pop("created_at", UNSET)

        updated_at = d.pop("updated_at", UNSET)

        _raw = d.pop("raw", UNSET)
        raw: Raw | Unset
        if isinstance(_raw, Unset):
            raw = UNSET
        else:
            raw = Raw.from_dict(_raw)

        sync_object_in = cls(
            object_id=object_id,
            object_type=object_type,
            title=title,
            content=content,
            excerpt=excerpt,
            document_id=document_id,
            document_title=document_title,
            page=page,
            tags=tags,
            links=links,
            color=color,
            created_at=created_at,
            updated_at=updated_at,
            raw=raw,
        )

        sync_object_in.additional_properties = d
        return sync_object_in

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
