from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.knowledge_type import KnowledgeType, check_knowledge_type
from ..types import UNSET, Unset

T = TypeVar("T", bound="KnowledgePointInput")


@_attrs_define
class KnowledgePointInput:
    """
    Attributes:
        name (str):
        id (None | str | Unset):
        client_ref (str | Unset):  Default: ''.
        type_ (KnowledgeType | Unset):
        module_id (str | Unset):  Default: ''.
        prerequisite_ids (list[str] | Unset):
        prerequisite_refs (list[str] | Unset):
        topic_source_ids (list[str] | Unset):
        topic_source_refs (list[str] | Unset):
    """

    name: str
    id: None | str | Unset = UNSET
    client_ref: str | Unset = ""
    type_: KnowledgeType | Unset = UNSET
    module_id: str | Unset = ""
    prerequisite_ids: list[str] | Unset = UNSET
    prerequisite_refs: list[str] | Unset = UNSET
    topic_source_ids: list[str] | Unset = UNSET
    topic_source_refs: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        id: None | str | Unset
        if isinstance(self.id, Unset):
            id = UNSET
        else:
            id = self.id

        client_ref = self.client_ref

        type_: str | Unset = UNSET
        if not isinstance(self.type_, Unset):
            type_ = self.type_

        module_id = self.module_id

        prerequisite_ids: list[str] | Unset = UNSET
        if not isinstance(self.prerequisite_ids, Unset):
            prerequisite_ids = self.prerequisite_ids

        prerequisite_refs: list[str] | Unset = UNSET
        if not isinstance(self.prerequisite_refs, Unset):
            prerequisite_refs = self.prerequisite_refs

        topic_source_ids: list[str] | Unset = UNSET
        if not isinstance(self.topic_source_ids, Unset):
            topic_source_ids = self.topic_source_ids

        topic_source_refs: list[str] | Unset = UNSET
        if not isinstance(self.topic_source_refs, Unset):
            topic_source_refs = self.topic_source_refs

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
            }
        )
        if id is not UNSET:
            field_dict["id"] = id
        if client_ref is not UNSET:
            field_dict["client_ref"] = client_ref
        if type_ is not UNSET:
            field_dict["type"] = type_
        if module_id is not UNSET:
            field_dict["module_id"] = module_id
        if prerequisite_ids is not UNSET:
            field_dict["prerequisite_ids"] = prerequisite_ids
        if prerequisite_refs is not UNSET:
            field_dict["prerequisite_refs"] = prerequisite_refs
        if topic_source_ids is not UNSET:
            field_dict["topic_source_ids"] = topic_source_ids
        if topic_source_refs is not UNSET:
            field_dict["topic_source_refs"] = topic_source_refs

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        def _parse_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        id = _parse_id(d.pop("id", UNSET))

        client_ref = d.pop("client_ref", UNSET)

        _type_ = d.pop("type", UNSET)
        type_: KnowledgeType | Unset
        if isinstance(_type_, Unset):
            type_ = UNSET
        else:
            type_ = check_knowledge_type(_type_)

        module_id = d.pop("module_id", UNSET)

        prerequisite_ids = cast(list[str], d.pop("prerequisite_ids", UNSET))

        prerequisite_refs = cast(list[str], d.pop("prerequisite_refs", UNSET))

        topic_source_ids = cast(list[str], d.pop("topic_source_ids", UNSET))

        topic_source_refs = cast(list[str], d.pop("topic_source_refs", UNSET))

        knowledge_point_input = cls(
            name=name,
            id=id,
            client_ref=client_ref,
            type_=type_,
            module_id=module_id,
            prerequisite_ids=prerequisite_ids,
            prerequisite_refs=prerequisite_refs,
            topic_source_ids=topic_source_ids,
            topic_source_refs=topic_source_refs,
        )

        knowledge_point_input.additional_properties = d
        return knowledge_point_input

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
