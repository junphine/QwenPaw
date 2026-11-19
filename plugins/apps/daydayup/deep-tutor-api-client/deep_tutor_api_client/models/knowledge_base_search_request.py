from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="KnowledgeBaseSearchRequest")


@_attrs_define
class KnowledgeBaseSearchRequest:
    """Request body for the knowledge-base RAG search open API.

    Attributes:
        query (str):
        top_k (int | None | Unset):
        rewrite (bool | None | Unset):
        document_keys (list[str] | None | Unset):
    """

    query: str
    top_k: int | None | Unset = UNSET
    rewrite: bool | None | Unset = UNSET
    document_keys: list[str] | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        query = self.query

        top_k: int | None | Unset
        if isinstance(self.top_k, Unset):
            top_k = UNSET
        else:
            top_k = self.top_k

        rewrite: bool | None | Unset
        if isinstance(self.rewrite, Unset):
            rewrite = UNSET
        else:
            rewrite = self.rewrite

        document_keys: list[str] | None | Unset
        if isinstance(self.document_keys, Unset):
            document_keys = UNSET
        elif isinstance(self.document_keys, list):
            document_keys = self.document_keys

        else:
            document_keys = self.document_keys

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "query": query,
            }
        )
        if top_k is not UNSET:
            field_dict["top_k"] = top_k
        if rewrite is not UNSET:
            field_dict["rewrite"] = rewrite
        if document_keys is not UNSET:
            field_dict["document_keys"] = document_keys

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        query = d.pop("query")

        def _parse_top_k(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        top_k = _parse_top_k(d.pop("top_k", UNSET))

        def _parse_rewrite(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        rewrite = _parse_rewrite(d.pop("rewrite", UNSET))

        def _parse_document_keys(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                document_keys_type_0 = cast(list[str], data)

                return document_keys_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        document_keys = _parse_document_keys(d.pop("document_keys", UNSET))

        knowledge_base_search_request = cls(
            query=query,
            top_k=top_k,
            rewrite=rewrite,
            document_keys=document_keys,
        )

        knowledge_base_search_request.additional_properties = d
        return knowledge_base_search_request

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
