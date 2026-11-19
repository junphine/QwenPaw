from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from .. import types
from ..types import UNSET, Unset

T = TypeVar("T", bound="BodyCreateKnowledgeBaseApiKnowledgeBasesPost")


@_attrs_define
class BodyCreateKnowledgeBaseApiKnowledgeBasesPost:
    """
    Attributes:
        name (str):
        files (list[str] | Unset):
        rag_provider (str | Unset):  Default: 'llamaindex'.
        pageindex_mode (str | Unset):  Default: ''.
        search_mode (str | Unset):  Default: ''.
        rel_paths (list[str] | Unset):
        indexing_llm (str | Unset):  Default: ''.
        embedding_model (str | Unset):  Default: ''.
        storage_workspace_id (None | str | Unset):
        description (str | Unset):  Default: ''.
    """

    name: str
    files: list[str] | Unset = UNSET
    rag_provider: str | Unset = "llamaindex"
    pageindex_mode: str | Unset = ""
    search_mode: str | Unset = ""
    rel_paths: list[str] | Unset = UNSET
    indexing_llm: str | Unset = ""
    embedding_model: str | Unset = ""
    storage_workspace_id: None | str | Unset = UNSET
    description: str | Unset = ""
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        files: list[str] | Unset = UNSET
        if not isinstance(self.files, Unset):
            files = self.files

        rag_provider = self.rag_provider

        pageindex_mode = self.pageindex_mode

        search_mode = self.search_mode

        rel_paths: list[str] | Unset = UNSET
        if not isinstance(self.rel_paths, Unset):
            rel_paths = self.rel_paths

        indexing_llm = self.indexing_llm

        embedding_model = self.embedding_model

        storage_workspace_id: None | str | Unset
        if isinstance(self.storage_workspace_id, Unset):
            storage_workspace_id = UNSET
        else:
            storage_workspace_id = self.storage_workspace_id

        description = self.description

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
            }
        )
        if files is not UNSET:
            field_dict["files"] = files
        if rag_provider is not UNSET:
            field_dict["rag_provider"] = rag_provider
        if pageindex_mode is not UNSET:
            field_dict["pageindex_mode"] = pageindex_mode
        if search_mode is not UNSET:
            field_dict["search_mode"] = search_mode
        if rel_paths is not UNSET:
            field_dict["rel_paths"] = rel_paths
        if indexing_llm is not UNSET:
            field_dict["indexing_llm"] = indexing_llm
        if embedding_model is not UNSET:
            field_dict["embedding_model"] = embedding_model
        if storage_workspace_id is not UNSET:
            field_dict["storage_workspace_id"] = storage_workspace_id
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    def to_multipart(self) -> types.RequestFiles:
        files: types.RequestFiles = []

        files.append(("name", (None, str(self.name).encode(), "text/plain")))

        if not isinstance(self.files, Unset):
            for files_item_element in self.files:
                files.append(("files", (None, str(files_item_element).encode(), "text/plain")))

        if not isinstance(self.rag_provider, Unset):
            files.append(("rag_provider", (None, str(self.rag_provider).encode(), "text/plain")))

        if not isinstance(self.pageindex_mode, Unset):
            files.append(("pageindex_mode", (None, str(self.pageindex_mode).encode(), "text/plain")))

        if not isinstance(self.search_mode, Unset):
            files.append(("search_mode", (None, str(self.search_mode).encode(), "text/plain")))

        if not isinstance(self.rel_paths, Unset):
            for rel_paths_item_element in self.rel_paths:
                files.append(("rel_paths", (None, str(rel_paths_item_element).encode(), "text/plain")))

        if not isinstance(self.indexing_llm, Unset):
            files.append(("indexing_llm", (None, str(self.indexing_llm).encode(), "text/plain")))

        if not isinstance(self.embedding_model, Unset):
            files.append(("embedding_model", (None, str(self.embedding_model).encode(), "text/plain")))

        if not isinstance(self.storage_workspace_id, Unset):
            if isinstance(self.storage_workspace_id, str):
                files.append(("storage_workspace_id", (None, str(self.storage_workspace_id).encode(), "text/plain")))
            else:
                files.append(("storage_workspace_id", (None, str(self.storage_workspace_id).encode(), "text/plain")))

        if not isinstance(self.description, Unset):
            files.append(("description", (None, str(self.description).encode(), "text/plain")))

        for prop_name, prop in self.additional_properties.items():
            files.append((prop_name, (None, str(prop).encode(), "text/plain")))

        return files

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        files = cast(list[str], d.pop("files", UNSET))

        rag_provider = d.pop("rag_provider", UNSET)

        pageindex_mode = d.pop("pageindex_mode", UNSET)

        search_mode = d.pop("search_mode", UNSET)

        rel_paths = cast(list[str], d.pop("rel_paths", UNSET))

        indexing_llm = d.pop("indexing_llm", UNSET)

        embedding_model = d.pop("embedding_model", UNSET)

        def _parse_storage_workspace_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        storage_workspace_id = _parse_storage_workspace_id(d.pop("storage_workspace_id", UNSET))

        description = d.pop("description", UNSET)

        body_create_knowledge_base_api_knowledge_bases_post = cls(
            name=name,
            files=files,
            rag_provider=rag_provider,
            pageindex_mode=pageindex_mode,
            search_mode=search_mode,
            rel_paths=rel_paths,
            indexing_llm=indexing_llm,
            embedding_model=embedding_model,
            storage_workspace_id=storage_workspace_id,
            description=description,
        )

        body_create_knowledge_base_api_knowledge_bases_post.additional_properties = d
        return body_create_knowledge_base_api_knowledge_bases_post

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
