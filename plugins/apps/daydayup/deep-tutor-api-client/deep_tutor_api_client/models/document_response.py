from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.document_response_blocks_type_0_item import DocumentResponseBlocksType0Item


T = TypeVar("T", bound="DocumentResponse")


@_attrs_define
class DocumentResponse:
    """
    Attributes:
        id (str):
        title (str | Unset):  Default: ''.
        content (str | Unset):  Default: ''.
        blocks (list[DocumentResponseBlocksType0Item] | None | Unset):
        schema_version (int | Unset):  Default: 1.
        revision (int | Unset):  Default: 0.
        parent_id (None | str | Unset):
        icon (str | Unset):  Default: ''.
        cover (str | Unset):  Default: ''.
        pinned (bool | Unset):  Default: False.
        applied_suggestion_ids (list[str] | Unset):
        created_at (float | Unset):
        updated_at (float | Unset):
    """

    id: str
    title: str | Unset = ""
    content: str | Unset = ""
    blocks: list[DocumentResponseBlocksType0Item] | None | Unset = UNSET
    schema_version: int | Unset = 1
    revision: int | Unset = 0
    parent_id: None | str | Unset = UNSET
    icon: str | Unset = ""
    cover: str | Unset = ""
    pinned: bool | Unset = False
    applied_suggestion_ids: list[str] | Unset = UNSET
    created_at: float | Unset = UNSET
    updated_at: float | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        title = self.title

        content = self.content

        blocks: list[dict[str, Any]] | None | Unset
        if isinstance(self.blocks, Unset):
            blocks = UNSET
        elif isinstance(self.blocks, list):
            blocks = []
            for blocks_type_0_item_data in self.blocks:
                blocks_type_0_item = blocks_type_0_item_data.to_dict()
                blocks.append(blocks_type_0_item)

        else:
            blocks = self.blocks

        schema_version = self.schema_version

        revision = self.revision

        parent_id: None | str | Unset
        if isinstance(self.parent_id, Unset):
            parent_id = UNSET
        else:
            parent_id = self.parent_id

        icon = self.icon

        cover = self.cover

        pinned = self.pinned

        applied_suggestion_ids: list[str] | Unset = UNSET
        if not isinstance(self.applied_suggestion_ids, Unset):
            applied_suggestion_ids = self.applied_suggestion_ids

        created_at = self.created_at

        updated_at = self.updated_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
            }
        )
        if title is not UNSET:
            field_dict["title"] = title
        if content is not UNSET:
            field_dict["content"] = content
        if blocks is not UNSET:
            field_dict["blocks"] = blocks
        if schema_version is not UNSET:
            field_dict["schema_version"] = schema_version
        if revision is not UNSET:
            field_dict["revision"] = revision
        if parent_id is not UNSET:
            field_dict["parent_id"] = parent_id
        if icon is not UNSET:
            field_dict["icon"] = icon
        if cover is not UNSET:
            field_dict["cover"] = cover
        if pinned is not UNSET:
            field_dict["pinned"] = pinned
        if applied_suggestion_ids is not UNSET:
            field_dict["applied_suggestion_ids"] = applied_suggestion_ids
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.document_response_blocks_type_0_item import DocumentResponseBlocksType0Item  # noqa: PLC0415

        d = dict(src_dict)
        id = d.pop("id")

        title = d.pop("title", UNSET)

        content = d.pop("content", UNSET)

        def _parse_blocks(data: object) -> list[DocumentResponseBlocksType0Item] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                blocks_type_0 = []
                _blocks_type_0 = data
                for blocks_type_0_item_data in _blocks_type_0:
                    blocks_type_0_item = DocumentResponseBlocksType0Item.from_dict(blocks_type_0_item_data)

                    blocks_type_0.append(blocks_type_0_item)

                return blocks_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[DocumentResponseBlocksType0Item] | None | Unset, data)

        blocks = _parse_blocks(d.pop("blocks", UNSET))

        schema_version = d.pop("schema_version", UNSET)

        revision = d.pop("revision", UNSET)

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

        applied_suggestion_ids = cast(list[str], d.pop("applied_suggestion_ids", UNSET))

        created_at = d.pop("created_at", UNSET)

        updated_at = d.pop("updated_at", UNSET)

        document_response = cls(
            id=id,
            title=title,
            content=content,
            blocks=blocks,
            schema_version=schema_version,
            revision=revision,
            parent_id=parent_id,
            icon=icon,
            cover=cover,
            pinned=pinned,
            applied_suggestion_ids=applied_suggestion_ids,
            created_at=created_at,
            updated_at=updated_at,
        )

        document_response.additional_properties = d
        return document_response

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
