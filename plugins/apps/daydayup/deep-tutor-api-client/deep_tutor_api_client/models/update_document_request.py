from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.update_document_request_blocks_type_0_item import UpdateDocumentRequestBlocksType0Item


T = TypeVar("T", bound="UpdateDocumentRequest")


@_attrs_define
class UpdateDocumentRequest:
    """
    Attributes:
        blocks (list[UpdateDocumentRequestBlocksType0Item] | None | Unset):
        expected_revision (int | None | Unset):
        parent_id (None | str | Unset):
        icon (str | Unset):  Default: ''.
        cover (str | Unset):  Default: ''.
        pinned (bool | Unset):  Default: False.
        title (None | str | Unset):
        content (None | str | Unset):
    """

    blocks: list[UpdateDocumentRequestBlocksType0Item] | None | Unset = UNSET
    expected_revision: int | None | Unset = UNSET
    parent_id: None | str | Unset = UNSET
    icon: str | Unset = ""
    cover: str | Unset = ""
    pinned: bool | Unset = False
    title: None | str | Unset = UNSET
    content: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
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

        expected_revision: int | None | Unset
        if isinstance(self.expected_revision, Unset):
            expected_revision = UNSET
        else:
            expected_revision = self.expected_revision

        parent_id: None | str | Unset
        if isinstance(self.parent_id, Unset):
            parent_id = UNSET
        else:
            parent_id = self.parent_id

        icon = self.icon

        cover = self.cover

        pinned = self.pinned

        title: None | str | Unset
        if isinstance(self.title, Unset):
            title = UNSET
        else:
            title = self.title

        content: None | str | Unset
        if isinstance(self.content, Unset):
            content = UNSET
        else:
            content = self.content

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if blocks is not UNSET:
            field_dict["blocks"] = blocks
        if expected_revision is not UNSET:
            field_dict["expected_revision"] = expected_revision
        if parent_id is not UNSET:
            field_dict["parent_id"] = parent_id
        if icon is not UNSET:
            field_dict["icon"] = icon
        if cover is not UNSET:
            field_dict["cover"] = cover
        if pinned is not UNSET:
            field_dict["pinned"] = pinned
        if title is not UNSET:
            field_dict["title"] = title
        if content is not UNSET:
            field_dict["content"] = content

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.update_document_request_blocks_type_0_item import (
            UpdateDocumentRequestBlocksType0Item,  # noqa: PLC0415
        )

        d = dict(src_dict)

        def _parse_blocks(data: object) -> list[UpdateDocumentRequestBlocksType0Item] | None | Unset:
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
                    blocks_type_0_item = UpdateDocumentRequestBlocksType0Item.from_dict(blocks_type_0_item_data)

                    blocks_type_0.append(blocks_type_0_item)

                return blocks_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[UpdateDocumentRequestBlocksType0Item] | None | Unset, data)

        blocks = _parse_blocks(d.pop("blocks", UNSET))

        def _parse_expected_revision(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        expected_revision = _parse_expected_revision(d.pop("expected_revision", UNSET))

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

        def _parse_title(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        title = _parse_title(d.pop("title", UNSET))

        def _parse_content(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        content = _parse_content(d.pop("content", UNSET))

        update_document_request = cls(
            blocks=blocks,
            expected_revision=expected_revision,
            parent_id=parent_id,
            icon=icon,
            cover=cover,
            pinned=pinned,
            title=title,
            content=content,
        )

        update_document_request.additional_properties = d
        return update_document_request

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
