from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.knowledge_base_info_metadata_type_0 import KnowledgeBaseInfoMetadataType0
    from ..models.knowledge_base_info_progress_type_0 import KnowledgeBaseInfoProgressType0
    from ..models.statistics import Statistics


T = TypeVar("T", bound="KnowledgeBaseInfo")


@_attrs_define
class KnowledgeBaseInfo:
    """
    Attributes:
        name (str):
        is_default (bool):
        statistics (Statistics):
        id (None | str | Unset):
        metadata (KnowledgeBaseInfoMetadataType0 | None | Unset):
        path (None | str | Unset):
        status (None | str | Unset):
        progress (KnowledgeBaseInfoProgressType0 | None | Unset):
        source (None | str | Unset):
        assigned (bool | Unset):  Default: False.
        read_only (bool | Unset):  Default: False.
        provenance_label (None | str | Unset):
        available (bool | Unset):  Default: True.
    """

    name: str
    is_default: bool
    statistics: Statistics
    id: None | str | Unset = UNSET
    metadata: KnowledgeBaseInfoMetadataType0 | None | Unset = UNSET
    path: None | str | Unset = UNSET
    status: None | str | Unset = UNSET
    progress: KnowledgeBaseInfoProgressType0 | None | Unset = UNSET
    source: None | str | Unset = UNSET
    assigned: bool | Unset = False
    read_only: bool | Unset = False
    provenance_label: None | str | Unset = UNSET
    available: bool | Unset = True
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.knowledge_base_info_metadata_type_0 import KnowledgeBaseInfoMetadataType0  # noqa: PLC0415
        from ..models.knowledge_base_info_progress_type_0 import KnowledgeBaseInfoProgressType0  # noqa: PLC0415

        name = self.name

        is_default = self.is_default

        statistics = self.statistics.to_dict()

        id: None | str | Unset
        if isinstance(self.id, Unset):
            id = UNSET
        else:
            id = self.id

        metadata: dict[str, Any] | None | Unset
        if isinstance(self.metadata, Unset):
            metadata = UNSET
        elif isinstance(self.metadata, KnowledgeBaseInfoMetadataType0):
            metadata = self.metadata.to_dict()
        else:
            metadata = self.metadata

        path: None | str | Unset
        if isinstance(self.path, Unset):
            path = UNSET
        else:
            path = self.path

        status: None | str | Unset
        if isinstance(self.status, Unset):
            status = UNSET
        else:
            status = self.status

        progress: dict[str, Any] | None | Unset
        if isinstance(self.progress, Unset):
            progress = UNSET
        elif isinstance(self.progress, KnowledgeBaseInfoProgressType0):
            progress = self.progress.to_dict()
        else:
            progress = self.progress

        source: None | str | Unset
        if isinstance(self.source, Unset):
            source = UNSET
        else:
            source = self.source

        assigned = self.assigned

        read_only = self.read_only

        provenance_label: None | str | Unset
        if isinstance(self.provenance_label, Unset):
            provenance_label = UNSET
        else:
            provenance_label = self.provenance_label

        available = self.available

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "is_default": is_default,
                "statistics": statistics,
            }
        )
        if id is not UNSET:
            field_dict["id"] = id
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if path is not UNSET:
            field_dict["path"] = path
        if status is not UNSET:
            field_dict["status"] = status
        if progress is not UNSET:
            field_dict["progress"] = progress
        if source is not UNSET:
            field_dict["source"] = source
        if assigned is not UNSET:
            field_dict["assigned"] = assigned
        if read_only is not UNSET:
            field_dict["read_only"] = read_only
        if provenance_label is not UNSET:
            field_dict["provenance_label"] = provenance_label
        if available is not UNSET:
            field_dict["available"] = available

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.knowledge_base_info_metadata_type_0 import KnowledgeBaseInfoMetadataType0  # noqa: PLC0415
        from ..models.knowledge_base_info_progress_type_0 import KnowledgeBaseInfoProgressType0  # noqa: PLC0415
        from ..models.statistics import Statistics  # noqa: PLC0415

        d = dict(src_dict)
        name = d.pop("name")

        is_default = d.pop("is_default")

        statistics = Statistics.from_dict(d.pop("statistics"))

        def _parse_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        id = _parse_id(d.pop("id", UNSET))

        def _parse_metadata(data: object) -> KnowledgeBaseInfoMetadataType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                metadata_type_0 = KnowledgeBaseInfoMetadataType0.from_dict(data)

                return metadata_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(KnowledgeBaseInfoMetadataType0 | None | Unset, data)

        metadata = _parse_metadata(d.pop("metadata", UNSET))

        def _parse_path(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        path = _parse_path(d.pop("path", UNSET))

        def _parse_status(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        status = _parse_status(d.pop("status", UNSET))

        def _parse_progress(data: object) -> KnowledgeBaseInfoProgressType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                progress_type_0 = KnowledgeBaseInfoProgressType0.from_dict(data)

                return progress_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(KnowledgeBaseInfoProgressType0 | None | Unset, data)

        progress = _parse_progress(d.pop("progress", UNSET))

        def _parse_source(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        source = _parse_source(d.pop("source", UNSET))

        assigned = d.pop("assigned", UNSET)

        read_only = d.pop("read_only", UNSET)

        def _parse_provenance_label(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        provenance_label = _parse_provenance_label(d.pop("provenance_label", UNSET))

        available = d.pop("available", UNSET)

        knowledge_base_info = cls(
            name=name,
            is_default=is_default,
            statistics=statistics,
            id=id,
            metadata=metadata,
            path=path,
            status=status,
            progress=progress,
            source=source,
            assigned=assigned,
            read_only=read_only,
            provenance_label=provenance_label,
            available=available,
        )

        knowledge_base_info.additional_properties = d
        return knowledge_base_info

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
