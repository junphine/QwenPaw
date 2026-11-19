from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.review_suggestion_request_blocks_type_0_item import ReviewSuggestionRequestBlocksType0Item


T = TypeVar("T", bound="ReviewSuggestionRequest")


@_attrs_define
class ReviewSuggestionRequest:
    """
    Attributes:
        accept (bool):
        blocks (list[ReviewSuggestionRequestBlocksType0Item] | None | Unset):
    """

    accept: bool
    blocks: list[ReviewSuggestionRequestBlocksType0Item] | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        accept = self.accept

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

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "accept": accept,
            }
        )
        if blocks is not UNSET:
            field_dict["blocks"] = blocks

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.review_suggestion_request_blocks_type_0_item import (
            ReviewSuggestionRequestBlocksType0Item,  # noqa: PLC0415
        )

        d = dict(src_dict)
        accept = d.pop("accept")

        def _parse_blocks(data: object) -> list[ReviewSuggestionRequestBlocksType0Item] | None | Unset:
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
                    blocks_type_0_item = ReviewSuggestionRequestBlocksType0Item.from_dict(blocks_type_0_item_data)

                    blocks_type_0.append(blocks_type_0_item)

                return blocks_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[ReviewSuggestionRequestBlocksType0Item] | None | Unset, data)

        blocks = _parse_blocks(d.pop("blocks", UNSET))

        review_suggestion_request = cls(
            accept=accept,
            blocks=blocks,
        )

        review_suggestion_request.additional_properties = d
        return review_suggestion_request

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
