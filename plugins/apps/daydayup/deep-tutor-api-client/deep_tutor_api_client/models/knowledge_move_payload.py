from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="KnowledgeMovePayload")


@_attrs_define
class KnowledgeMovePayload:
    """
    Attributes:
        source_id (str):
        target_workspace_id (str | Unset):  Default: ''.
    """

    source_id: str
    target_workspace_id: str | Unset = ""
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        source_id = self.source_id

        target_workspace_id = self.target_workspace_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "source_id": source_id,
            }
        )
        if target_workspace_id is not UNSET:
            field_dict["target_workspace_id"] = target_workspace_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        source_id = d.pop("source_id")

        target_workspace_id = d.pop("target_workspace_id", UNSET)

        knowledge_move_payload = cls(
            source_id=source_id,
            target_workspace_id=target_workspace_id,
        )

        knowledge_move_payload.additional_properties = d
        return knowledge_move_payload

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
