from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.add_record_request_record_type import AddRecordRequestRecordType, check_add_record_request_record_type
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.metadata import Metadata


T = TypeVar("T", bound="AddRecordRequest")


@_attrs_define
class AddRecordRequest:
    """Add record request

    Attributes:
        notebook_ids (list[str]):
        record_type (AddRecordRequestRecordType):
        title (str):
        user_query (str):
        output (str):
        summary (str | Unset):  Default: ''.
        metadata (Metadata | Unset):
        kb_name (None | str | Unset):
    """

    notebook_ids: list[str]
    record_type: AddRecordRequestRecordType
    title: str
    user_query: str
    output: str
    summary: str | Unset = ""
    metadata: Metadata | Unset = UNSET
    kb_name: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        notebook_ids = self.notebook_ids

        record_type: str = self.record_type

        title = self.title

        user_query = self.user_query

        output = self.output

        summary = self.summary

        metadata: dict[str, Any] | Unset = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        kb_name: None | str | Unset
        if isinstance(self.kb_name, Unset):
            kb_name = UNSET
        else:
            kb_name = self.kb_name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "notebook_ids": notebook_ids,
                "record_type": record_type,
                "title": title,
                "user_query": user_query,
                "output": output,
            }
        )
        if summary is not UNSET:
            field_dict["summary"] = summary
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if kb_name is not UNSET:
            field_dict["kb_name"] = kb_name

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.metadata import Metadata  # noqa: PLC0415

        d = dict(src_dict)
        notebook_ids = cast(list[str], d.pop("notebook_ids"))

        record_type = check_add_record_request_record_type(d.pop("record_type"))

        title = d.pop("title")

        user_query = d.pop("user_query")

        output = d.pop("output")

        summary = d.pop("summary", UNSET)

        _metadata = d.pop("metadata", UNSET)
        metadata: Metadata | Unset
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = Metadata.from_dict(_metadata)

        def _parse_kb_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        kb_name = _parse_kb_name(d.pop("kb_name", UNSET))

        add_record_request = cls(
            notebook_ids=notebook_ids,
            record_type=record_type,
            title=title,
            user_query=user_query,
            output=output,
            summary=summary,
            metadata=metadata,
            kb_name=kb_name,
        )

        add_record_request.additional_properties = d
        return add_record_request

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
