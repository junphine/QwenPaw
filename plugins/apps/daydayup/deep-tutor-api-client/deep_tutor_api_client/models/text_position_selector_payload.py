from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="TextPositionSelectorPayload")


@_attrs_define
class TextPositionSelectorPayload:
    """
    Attributes:
        type_ (Literal['TextPositionSelector']):
        start (int):
        end (int):
    """

    type_: Literal["TextPositionSelector"]
    start: int
    end: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_

        start = self.start

        end = self.end

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "start": start,
                "end": end,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        type_ = cast(Literal["TextPositionSelector"], d.pop("type"))
        if type_ != "TextPositionSelector":
            raise ValueError(f"type must match const 'TextPositionSelector', got '{type_}'")

        start = d.pop("start")

        end = d.pop("end")

        text_position_selector_payload = cls(
            type_=type_,
            start=start,
            end=end,
        )

        text_position_selector_payload.additional_properties = d
        return text_position_selector_payload

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
