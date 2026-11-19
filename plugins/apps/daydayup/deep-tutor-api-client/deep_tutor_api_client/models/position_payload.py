from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PositionPayload")


@_attrs_define
class PositionPayload:
    """
    Attributes:
        locator (int):
        source_anchor (str | Unset):  Default: ''.
        percentage (float | None | Unset):
    """

    locator: int
    source_anchor: str | Unset = ""
    percentage: float | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        locator = self.locator

        source_anchor = self.source_anchor

        percentage: float | None | Unset
        if isinstance(self.percentage, Unset):
            percentage = UNSET
        else:
            percentage = self.percentage

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "locator": locator,
            }
        )
        if source_anchor is not UNSET:
            field_dict["source_anchor"] = source_anchor
        if percentage is not UNSET:
            field_dict["percentage"] = percentage

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        locator = d.pop("locator")

        source_anchor = d.pop("source_anchor", UNSET)

        def _parse_percentage(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        percentage = _parse_percentage(d.pop("percentage", UNSET))

        position_payload = cls(
            locator=locator,
            source_anchor=source_anchor,
            percentage=percentage,
        )

        position_payload.additional_properties = d
        return position_payload

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
