from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="NotebookRecordInput")


@_attrs_define
class NotebookRecordInput:
    """
    Attributes:
        id (str):
        type_ (str | Unset):  Default: 'note'.
        title (str | Unset):  Default: ''.
        output (str | Unset):  Default: ''.
    """

    id: str
    type_: str | Unset = "note"
    title: str | Unset = ""
    output: str | Unset = ""
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        type_ = self.type_

        title = self.title

        output = self.output

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
            }
        )
        if type_ is not UNSET:
            field_dict["type"] = type_
        if title is not UNSET:
            field_dict["title"] = title
        if output is not UNSET:
            field_dict["output"] = output

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        type_ = d.pop("type", UNSET)

        title = d.pop("title", UNSET)

        output = d.pop("output", UNSET)

        notebook_record_input = cls(
            id=id,
            type_=type_,
            title=title,
            output=output,
        )

        notebook_record_input.additional_properties = d
        return notebook_record_input

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
