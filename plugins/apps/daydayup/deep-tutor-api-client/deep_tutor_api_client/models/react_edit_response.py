from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ReactEditResponse")


@_attrs_define
class ReactEditResponse:
    """
    Attributes:
        edited_text (str):
        operation_id (str):
        tools_used (list[str] | Unset):
    """

    edited_text: str
    operation_id: str
    tools_used: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        edited_text = self.edited_text

        operation_id = self.operation_id

        tools_used: list[str] | Unset = UNSET
        if not isinstance(self.tools_used, Unset):
            tools_used = self.tools_used

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "edited_text": edited_text,
                "operation_id": operation_id,
            }
        )
        if tools_used is not UNSET:
            field_dict["tools_used"] = tools_used

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        edited_text = d.pop("edited_text")

        operation_id = d.pop("operation_id")

        tools_used = cast(list[str], d.pop("tools_used", UNSET))

        react_edit_response = cls(
            edited_text=edited_text,
            operation_id=operation_id,
            tools_used=tools_used,
        )

        react_edit_response.additional_properties = d
        return react_edit_response

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
