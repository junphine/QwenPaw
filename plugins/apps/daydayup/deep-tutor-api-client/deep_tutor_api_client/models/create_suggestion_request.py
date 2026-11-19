from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.create_suggestion_request_blocks_type_0_item import CreateSuggestionRequestBlocksType0Item
    from ..models.create_suggestion_request_expected_original_type_0 import CreateSuggestionRequestExpectedOriginalType0


T = TypeVar("T", bound="CreateSuggestionRequest")


@_attrs_define
class CreateSuggestionRequest:
    """
    Attributes:
        operation (str | Unset):  Default: 'insert'.
        block_id (str | Unset):  Default: ''.
        markdown (str | Unset):  Default: ''.
        explanation (str | Unset):  Default: ''.
        blocks (list[CreateSuggestionRequestBlocksType0Item] | None | Unset):
        expected_original (CreateSuggestionRequestExpectedOriginalType0 | None | Unset):
        source_turn_id (str | Unset):  Default: ''.
    """

    operation: str | Unset = "insert"
    block_id: str | Unset = ""
    markdown: str | Unset = ""
    explanation: str | Unset = ""
    blocks: list[CreateSuggestionRequestBlocksType0Item] | None | Unset = UNSET
    expected_original: CreateSuggestionRequestExpectedOriginalType0 | None | Unset = UNSET
    source_turn_id: str | Unset = ""
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.create_suggestion_request_expected_original_type_0 import (
            CreateSuggestionRequestExpectedOriginalType0,  # noqa: PLC0415
        )

        operation = self.operation

        block_id = self.block_id

        markdown = self.markdown

        explanation = self.explanation

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

        expected_original: dict[str, Any] | None | Unset
        if isinstance(self.expected_original, Unset):
            expected_original = UNSET
        elif isinstance(self.expected_original, CreateSuggestionRequestExpectedOriginalType0):
            expected_original = self.expected_original.to_dict()
        else:
            expected_original = self.expected_original

        source_turn_id = self.source_turn_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if operation is not UNSET:
            field_dict["operation"] = operation
        if block_id is not UNSET:
            field_dict["block_id"] = block_id
        if markdown is not UNSET:
            field_dict["markdown"] = markdown
        if explanation is not UNSET:
            field_dict["explanation"] = explanation
        if blocks is not UNSET:
            field_dict["blocks"] = blocks
        if expected_original is not UNSET:
            field_dict["expected_original"] = expected_original
        if source_turn_id is not UNSET:
            field_dict["source_turn_id"] = source_turn_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.create_suggestion_request_blocks_type_0_item import (
            CreateSuggestionRequestBlocksType0Item,  # noqa: PLC0415
        )
        from ..models.create_suggestion_request_expected_original_type_0 import (
            CreateSuggestionRequestExpectedOriginalType0,  # noqa: PLC0415
        )

        d = dict(src_dict)
        operation = d.pop("operation", UNSET)

        block_id = d.pop("block_id", UNSET)

        markdown = d.pop("markdown", UNSET)

        explanation = d.pop("explanation", UNSET)

        def _parse_blocks(data: object) -> list[CreateSuggestionRequestBlocksType0Item] | None | Unset:
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
                    blocks_type_0_item = CreateSuggestionRequestBlocksType0Item.from_dict(blocks_type_0_item_data)

                    blocks_type_0.append(blocks_type_0_item)

                return blocks_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[CreateSuggestionRequestBlocksType0Item] | None | Unset, data)

        blocks = _parse_blocks(d.pop("blocks", UNSET))

        def _parse_expected_original(data: object) -> CreateSuggestionRequestExpectedOriginalType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                expected_original_type_0 = CreateSuggestionRequestExpectedOriginalType0.from_dict(data)

                return expected_original_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(CreateSuggestionRequestExpectedOriginalType0 | None | Unset, data)

        expected_original = _parse_expected_original(d.pop("expected_original", UNSET))

        source_turn_id = d.pop("source_turn_id", UNSET)

        create_suggestion_request = cls(
            operation=operation,
            block_id=block_id,
            markdown=markdown,
            explanation=explanation,
            blocks=blocks,
            expected_original=expected_original,
            source_turn_id=source_turn_id,
        )

        create_suggestion_request.additional_properties = d
        return create_suggestion_request

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
