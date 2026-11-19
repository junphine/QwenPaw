from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.update_record_request_metadata_type_0 import UpdateRecordRequestMetadataType0


T = TypeVar("T", bound="UpdateRecordRequest")


@_attrs_define
class UpdateRecordRequest:
    """Update an existing notebook record.

    Only the fields the client actually sends are forwarded (see
    ``exclude_unset`` at the call site), which is what keeps ``kb_name``
    from being wiped by a request that merely renames the record.

        Attributes:
            title (None | str | Unset):
            summary (None | str | Unset):
            user_query (None | str | Unset):
            output (None | str | Unset):
            metadata (None | Unset | UpdateRecordRequestMetadataType0):
            kb_name (None | str | Unset):
    """

    title: None | str | Unset = UNSET
    summary: None | str | Unset = UNSET
    user_query: None | str | Unset = UNSET
    output: None | str | Unset = UNSET
    metadata: None | Unset | UpdateRecordRequestMetadataType0 = UNSET
    kb_name: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.update_record_request_metadata_type_0 import UpdateRecordRequestMetadataType0  # noqa: PLC0415

        title: None | str | Unset
        if isinstance(self.title, Unset):
            title = UNSET
        else:
            title = self.title

        summary: None | str | Unset
        if isinstance(self.summary, Unset):
            summary = UNSET
        else:
            summary = self.summary

        user_query: None | str | Unset
        if isinstance(self.user_query, Unset):
            user_query = UNSET
        else:
            user_query = self.user_query

        output: None | str | Unset
        if isinstance(self.output, Unset):
            output = UNSET
        else:
            output = self.output

        metadata: dict[str, Any] | None | Unset
        if isinstance(self.metadata, Unset):
            metadata = UNSET
        elif isinstance(self.metadata, UpdateRecordRequestMetadataType0):
            metadata = self.metadata.to_dict()
        else:
            metadata = self.metadata

        kb_name: None | str | Unset
        if isinstance(self.kb_name, Unset):
            kb_name = UNSET
        else:
            kb_name = self.kb_name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if title is not UNSET:
            field_dict["title"] = title
        if summary is not UNSET:
            field_dict["summary"] = summary
        if user_query is not UNSET:
            field_dict["user_query"] = user_query
        if output is not UNSET:
            field_dict["output"] = output
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if kb_name is not UNSET:
            field_dict["kb_name"] = kb_name

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.update_record_request_metadata_type_0 import UpdateRecordRequestMetadataType0  # noqa: PLC0415

        d = dict(src_dict)

        def _parse_title(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        title = _parse_title(d.pop("title", UNSET))

        def _parse_summary(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        summary = _parse_summary(d.pop("summary", UNSET))

        def _parse_user_query(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        user_query = _parse_user_query(d.pop("user_query", UNSET))

        def _parse_output(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        output = _parse_output(d.pop("output", UNSET))

        def _parse_metadata(data: object) -> None | Unset | UpdateRecordRequestMetadataType0:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                metadata_type_0 = UpdateRecordRequestMetadataType0.from_dict(data)

                return metadata_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UpdateRecordRequestMetadataType0, data)

        metadata = _parse_metadata(d.pop("metadata", UNSET))

        def _parse_kb_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        kb_name = _parse_kb_name(d.pop("kb_name", UNSET))

        update_record_request = cls(
            title=title,
            summary=summary,
            user_query=user_query,
            output=output,
            metadata=metadata,
            kb_name=kb_name,
        )

        update_record_request.additional_properties = d
        return update_record_request

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
