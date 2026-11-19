from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.ima_knowledge_base_summary import ImaKnowledgeBaseSummary


T = TypeVar("T", bound="ListImaResponse")


@_attrs_define
class ListImaResponse:
    """
    Attributes:
        knowledge_bases (list[ImaKnowledgeBaseSummary]):
        next_cursor (str):
        is_end (bool):
    """

    knowledge_bases: list[ImaKnowledgeBaseSummary]
    next_cursor: str
    is_end: bool
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        knowledge_bases = []
        for knowledge_bases_item_data in self.knowledge_bases:
            knowledge_bases_item = knowledge_bases_item_data.to_dict()
            knowledge_bases.append(knowledge_bases_item)

        next_cursor = self.next_cursor

        is_end = self.is_end

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "knowledge_bases": knowledge_bases,
                "next_cursor": next_cursor,
                "is_end": is_end,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.ima_knowledge_base_summary import ImaKnowledgeBaseSummary  # noqa: PLC0415

        d = dict(src_dict)
        knowledge_bases = []
        _knowledge_bases = d.pop("knowledge_bases")
        for knowledge_bases_item_data in _knowledge_bases:
            knowledge_bases_item = ImaKnowledgeBaseSummary.from_dict(knowledge_bases_item_data)

            knowledge_bases.append(knowledge_bases_item)

        next_cursor = d.pop("next_cursor")

        is_end = d.pop("is_end")

        list_ima_response = cls(
            knowledge_bases=knowledge_bases,
            next_cursor=next_cursor,
            is_end=is_end,
        )

        list_ima_response.additional_properties = d
        return list_ima_response

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
