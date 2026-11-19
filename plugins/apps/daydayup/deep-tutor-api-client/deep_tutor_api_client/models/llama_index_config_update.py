from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="LlamaIndexConfigUpdate")


@_attrs_define
class LlamaIndexConfigUpdate:
    """Partial update for the LlamaIndex engine knobs (omitted fields kept).

    Attributes:
        retrieval_profile (None | str | Unset):
        top_k (int | None | Unset):
        vector_top_k_multiplier (int | None | Unset):
        bm25_top_k_multiplier (int | None | Unset):
        reranker_model (None | str | Unset):
        rerank_top_k (int | None | Unset):
        vector_index_type (None | str | Unset):
        hnsw_m (int | None | Unset):
        hnsw_ef_construction (int | None | Unset):
        hnsw_ef_search (int | None | Unset):
        chunk_size (int | None | Unset):
        chunk_overlap (int | None | Unset):
        image_description_concurrency (int | None | Unset):
        image_description_batch_size (int | None | Unset):
        image_description_timeout_seconds (int | None | Unset):
    """

    retrieval_profile: None | str | Unset = UNSET
    top_k: int | None | Unset = UNSET
    vector_top_k_multiplier: int | None | Unset = UNSET
    bm25_top_k_multiplier: int | None | Unset = UNSET
    reranker_model: None | str | Unset = UNSET
    rerank_top_k: int | None | Unset = UNSET
    vector_index_type: None | str | Unset = UNSET
    hnsw_m: int | None | Unset = UNSET
    hnsw_ef_construction: int | None | Unset = UNSET
    hnsw_ef_search: int | None | Unset = UNSET
    chunk_size: int | None | Unset = UNSET
    chunk_overlap: int | None | Unset = UNSET
    image_description_concurrency: int | None | Unset = UNSET
    image_description_batch_size: int | None | Unset = UNSET
    image_description_timeout_seconds: int | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        retrieval_profile: None | str | Unset
        if isinstance(self.retrieval_profile, Unset):
            retrieval_profile = UNSET
        else:
            retrieval_profile = self.retrieval_profile

        top_k: int | None | Unset
        if isinstance(self.top_k, Unset):
            top_k = UNSET
        else:
            top_k = self.top_k

        vector_top_k_multiplier: int | None | Unset
        if isinstance(self.vector_top_k_multiplier, Unset):
            vector_top_k_multiplier = UNSET
        else:
            vector_top_k_multiplier = self.vector_top_k_multiplier

        bm25_top_k_multiplier: int | None | Unset
        if isinstance(self.bm25_top_k_multiplier, Unset):
            bm25_top_k_multiplier = UNSET
        else:
            bm25_top_k_multiplier = self.bm25_top_k_multiplier

        reranker_model: None | str | Unset
        if isinstance(self.reranker_model, Unset):
            reranker_model = UNSET
        else:
            reranker_model = self.reranker_model

        rerank_top_k: int | None | Unset
        if isinstance(self.rerank_top_k, Unset):
            rerank_top_k = UNSET
        else:
            rerank_top_k = self.rerank_top_k

        vector_index_type: None | str | Unset
        if isinstance(self.vector_index_type, Unset):
            vector_index_type = UNSET
        else:
            vector_index_type = self.vector_index_type

        hnsw_m: int | None | Unset
        if isinstance(self.hnsw_m, Unset):
            hnsw_m = UNSET
        else:
            hnsw_m = self.hnsw_m

        hnsw_ef_construction: int | None | Unset
        if isinstance(self.hnsw_ef_construction, Unset):
            hnsw_ef_construction = UNSET
        else:
            hnsw_ef_construction = self.hnsw_ef_construction

        hnsw_ef_search: int | None | Unset
        if isinstance(self.hnsw_ef_search, Unset):
            hnsw_ef_search = UNSET
        else:
            hnsw_ef_search = self.hnsw_ef_search

        chunk_size: int | None | Unset
        if isinstance(self.chunk_size, Unset):
            chunk_size = UNSET
        else:
            chunk_size = self.chunk_size

        chunk_overlap: int | None | Unset
        if isinstance(self.chunk_overlap, Unset):
            chunk_overlap = UNSET
        else:
            chunk_overlap = self.chunk_overlap

        image_description_concurrency: int | None | Unset
        if isinstance(self.image_description_concurrency, Unset):
            image_description_concurrency = UNSET
        else:
            image_description_concurrency = self.image_description_concurrency

        image_description_batch_size: int | None | Unset
        if isinstance(self.image_description_batch_size, Unset):
            image_description_batch_size = UNSET
        else:
            image_description_batch_size = self.image_description_batch_size

        image_description_timeout_seconds: int | None | Unset
        if isinstance(self.image_description_timeout_seconds, Unset):
            image_description_timeout_seconds = UNSET
        else:
            image_description_timeout_seconds = self.image_description_timeout_seconds

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if retrieval_profile is not UNSET:
            field_dict["retrieval_profile"] = retrieval_profile
        if top_k is not UNSET:
            field_dict["top_k"] = top_k
        if vector_top_k_multiplier is not UNSET:
            field_dict["vector_top_k_multiplier"] = vector_top_k_multiplier
        if bm25_top_k_multiplier is not UNSET:
            field_dict["bm25_top_k_multiplier"] = bm25_top_k_multiplier
        if reranker_model is not UNSET:
            field_dict["reranker_model"] = reranker_model
        if rerank_top_k is not UNSET:
            field_dict["rerank_top_k"] = rerank_top_k
        if vector_index_type is not UNSET:
            field_dict["vector_index_type"] = vector_index_type
        if hnsw_m is not UNSET:
            field_dict["hnsw_m"] = hnsw_m
        if hnsw_ef_construction is not UNSET:
            field_dict["hnsw_ef_construction"] = hnsw_ef_construction
        if hnsw_ef_search is not UNSET:
            field_dict["hnsw_ef_search"] = hnsw_ef_search
        if chunk_size is not UNSET:
            field_dict["chunk_size"] = chunk_size
        if chunk_overlap is not UNSET:
            field_dict["chunk_overlap"] = chunk_overlap
        if image_description_concurrency is not UNSET:
            field_dict["image_description_concurrency"] = image_description_concurrency
        if image_description_batch_size is not UNSET:
            field_dict["image_description_batch_size"] = image_description_batch_size
        if image_description_timeout_seconds is not UNSET:
            field_dict["image_description_timeout_seconds"] = image_description_timeout_seconds

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_retrieval_profile(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        retrieval_profile = _parse_retrieval_profile(d.pop("retrieval_profile", UNSET))

        def _parse_top_k(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        top_k = _parse_top_k(d.pop("top_k", UNSET))

        def _parse_vector_top_k_multiplier(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        vector_top_k_multiplier = _parse_vector_top_k_multiplier(d.pop("vector_top_k_multiplier", UNSET))

        def _parse_bm25_top_k_multiplier(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        bm25_top_k_multiplier = _parse_bm25_top_k_multiplier(d.pop("bm25_top_k_multiplier", UNSET))

        def _parse_reranker_model(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        reranker_model = _parse_reranker_model(d.pop("reranker_model", UNSET))

        def _parse_rerank_top_k(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        rerank_top_k = _parse_rerank_top_k(d.pop("rerank_top_k", UNSET))

        def _parse_vector_index_type(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        vector_index_type = _parse_vector_index_type(d.pop("vector_index_type", UNSET))

        def _parse_hnsw_m(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        hnsw_m = _parse_hnsw_m(d.pop("hnsw_m", UNSET))

        def _parse_hnsw_ef_construction(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        hnsw_ef_construction = _parse_hnsw_ef_construction(d.pop("hnsw_ef_construction", UNSET))

        def _parse_hnsw_ef_search(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        hnsw_ef_search = _parse_hnsw_ef_search(d.pop("hnsw_ef_search", UNSET))

        def _parse_chunk_size(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        chunk_size = _parse_chunk_size(d.pop("chunk_size", UNSET))

        def _parse_chunk_overlap(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        chunk_overlap = _parse_chunk_overlap(d.pop("chunk_overlap", UNSET))

        def _parse_image_description_concurrency(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        image_description_concurrency = _parse_image_description_concurrency(
            d.pop("image_description_concurrency", UNSET)
        )

        def _parse_image_description_batch_size(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        image_description_batch_size = _parse_image_description_batch_size(d.pop("image_description_batch_size", UNSET))

        def _parse_image_description_timeout_seconds(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        image_description_timeout_seconds = _parse_image_description_timeout_seconds(
            d.pop("image_description_timeout_seconds", UNSET)
        )

        llama_index_config_update = cls(
            retrieval_profile=retrieval_profile,
            top_k=top_k,
            vector_top_k_multiplier=vector_top_k_multiplier,
            bm25_top_k_multiplier=bm25_top_k_multiplier,
            reranker_model=reranker_model,
            rerank_top_k=rerank_top_k,
            vector_index_type=vector_index_type,
            hnsw_m=hnsw_m,
            hnsw_ef_construction=hnsw_ef_construction,
            hnsw_ef_search=hnsw_ef_search,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            image_description_concurrency=image_description_concurrency,
            image_description_batch_size=image_description_batch_size,
            image_description_timeout_seconds=image_description_timeout_seconds,
        )

        llama_index_config_update.additional_properties = d
        return llama_index_config_update

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
