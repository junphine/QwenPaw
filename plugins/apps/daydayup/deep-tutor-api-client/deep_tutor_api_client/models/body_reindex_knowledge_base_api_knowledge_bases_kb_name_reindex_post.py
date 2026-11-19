from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="BodyReindexKnowledgeBaseApiKnowledgeBasesKbNameReindexPost")


@_attrs_define
class BodyReindexKnowledgeBaseApiKnowledgeBasesKbNameReindexPost:
    """
    Attributes:
        indexing_llm (str | Unset):  Default: ''.
        config_fingerprint (str | Unset):  Default: ''.
        embedding_model (str | Unset):  Default: ''.
    """

    indexing_llm: str | Unset = ""
    config_fingerprint: str | Unset = ""
    embedding_model: str | Unset = ""
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        indexing_llm = self.indexing_llm

        config_fingerprint = self.config_fingerprint

        embedding_model = self.embedding_model

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if indexing_llm is not UNSET:
            field_dict["indexing_llm"] = indexing_llm
        if config_fingerprint is not UNSET:
            field_dict["config_fingerprint"] = config_fingerprint
        if embedding_model is not UNSET:
            field_dict["embedding_model"] = embedding_model

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        indexing_llm = d.pop("indexing_llm", UNSET)

        config_fingerprint = d.pop("config_fingerprint", UNSET)

        embedding_model = d.pop("embedding_model", UNSET)

        body_reindex_knowledge_base_api_knowledge_bases_kb_name_reindex_post = cls(
            indexing_llm=indexing_llm,
            config_fingerprint=config_fingerprint,
            embedding_model=embedding_model,
        )

        body_reindex_knowledge_base_api_knowledge_bases_kb_name_reindex_post.additional_properties = d
        return body_reindex_knowledge_base_api_knowledge_bases_kb_name_reindex_post

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
