from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.intervals import Intervals


T = TypeVar("T", bound="ReviewStrategyRequest")


@_attrs_define
class ReviewStrategyRequest:
    """Create/edit a custom review strategy: per-round intervals per type.

    Attributes:
        name (str):
        intervals (Intervals):
        description (str | Unset):  Default: ''.
        desired_retention (float | None | Unset):
    """

    name: str
    intervals: Intervals
    description: str | Unset = ""
    desired_retention: float | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        intervals = self.intervals.to_dict()

        description = self.description

        desired_retention: float | None | Unset
        if isinstance(self.desired_retention, Unset):
            desired_retention = UNSET
        else:
            desired_retention = self.desired_retention

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "intervals": intervals,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if desired_retention is not UNSET:
            field_dict["desired_retention"] = desired_retention

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.intervals import Intervals  # noqa: PLC0415

        d = dict(src_dict)
        name = d.pop("name")

        intervals = Intervals.from_dict(d.pop("intervals"))

        description = d.pop("description", UNSET)

        def _parse_desired_retention(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        desired_retention = _parse_desired_retention(d.pop("desired_retention", UNSET))

        review_strategy_request = cls(
            name=name,
            intervals=intervals,
            description=description,
            desired_retention=desired_retention,
        )

        review_strategy_request.additional_properties = d
        return review_strategy_request

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
