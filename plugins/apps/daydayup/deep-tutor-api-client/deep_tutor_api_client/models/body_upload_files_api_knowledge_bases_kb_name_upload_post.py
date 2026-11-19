from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from .. import types
from ..types import UNSET, Unset

T = TypeVar("T", bound="BodyUploadFilesApiKnowledgeBasesKbNameUploadPost")


@_attrs_define
class BodyUploadFilesApiKnowledgeBasesKbNameUploadPost:
    """
    Attributes:
        files (list[str]):
        rag_provider (str | Unset):
        rel_paths (list[str] | Unset):
        dest_subdir (str | Unset):
        image_analysis (bool | None | Unset): Require image analysis with the pinned VLM; false skips images, omitted
            follows the pinned policy.
    """

    files: list[str]
    rag_provider: str | Unset = UNSET
    rel_paths: list[str] | Unset = UNSET
    dest_subdir: str | Unset = UNSET
    image_analysis: bool | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        files = self.files

        rag_provider = self.rag_provider

        rel_paths: list[str] | Unset = UNSET
        if not isinstance(self.rel_paths, Unset):
            rel_paths = self.rel_paths

        dest_subdir = self.dest_subdir

        image_analysis: bool | None | Unset
        if isinstance(self.image_analysis, Unset):
            image_analysis = UNSET
        else:
            image_analysis = self.image_analysis

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "files": files,
            }
        )
        if rag_provider is not UNSET:
            field_dict["rag_provider"] = rag_provider
        if rel_paths is not UNSET:
            field_dict["rel_paths"] = rel_paths
        if dest_subdir is not UNSET:
            field_dict["dest_subdir"] = dest_subdir
        if image_analysis is not UNSET:
            field_dict["image_analysis"] = image_analysis

        return field_dict

    def to_multipart(self) -> types.RequestFiles:
        files: types.RequestFiles = []

        for files_item_element in self.files:
            files.append(("files", (None, str(files_item_element).encode(), "text/plain")))

        if not isinstance(self.rag_provider, Unset):
            files.append(("rag_provider", (None, str(self.rag_provider).encode(), "text/plain")))

        if not isinstance(self.rel_paths, Unset):
            for rel_paths_item_element in self.rel_paths:
                files.append(("rel_paths", (None, str(rel_paths_item_element).encode(), "text/plain")))

        if not isinstance(self.dest_subdir, Unset):
            files.append(("dest_subdir", (None, str(self.dest_subdir).encode(), "text/plain")))

        if not isinstance(self.image_analysis, Unset):
            if isinstance(self.image_analysis, bool):
                files.append(("image_analysis", (None, str(self.image_analysis).encode(), "text/plain")))
            else:
                files.append(("image_analysis", (None, str(self.image_analysis).encode(), "text/plain")))

        for prop_name, prop in self.additional_properties.items():
            files.append((prop_name, (None, str(prop).encode(), "text/plain")))

        return files

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        files = cast(list[str], d.pop("files"))

        rag_provider = d.pop("rag_provider", UNSET)

        rel_paths = cast(list[str], d.pop("rel_paths", UNSET))

        dest_subdir = d.pop("dest_subdir", UNSET)

        def _parse_image_analysis(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        image_analysis = _parse_image_analysis(d.pop("image_analysis", UNSET))

        body_upload_files_api_knowledge_bases_kb_name_upload_post = cls(
            files=files,
            rag_provider=rag_provider,
            rel_paths=rel_paths,
            dest_subdir=dest_subdir,
            image_analysis=image_analysis,
        )

        body_upload_files_api_knowledge_bases_kb_name_upload_post.additional_properties = d
        return body_upload_files_api_knowledge_bases_kb_name_upload_post

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
