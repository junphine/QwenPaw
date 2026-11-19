from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.automation_run import AutomationRun
    from ..models.footprint_day import FootprintDay
    from ..models.review_day import ReviewDay


T = TypeVar("T", bound="CalendarLayers")


@_attrs_define
class CalendarLayers:
    """
    Attributes:
        workspace_id (str):
        reviews (list[ReviewDay] | Unset):
        automations (list[AutomationRun] | Unset):
        footprints (list[FootprintDay] | Unset):
    """

    workspace_id: str
    reviews: list[ReviewDay] | Unset = UNSET
    automations: list[AutomationRun] | Unset = UNSET
    footprints: list[FootprintDay] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        workspace_id = self.workspace_id

        reviews: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.reviews, Unset):
            reviews = []
            for reviews_item_data in self.reviews:
                reviews_item = reviews_item_data.to_dict()
                reviews.append(reviews_item)

        automations: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.automations, Unset):
            automations = []
            for automations_item_data in self.automations:
                automations_item = automations_item_data.to_dict()
                automations.append(automations_item)

        footprints: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.footprints, Unset):
            footprints = []
            for footprints_item_data in self.footprints:
                footprints_item = footprints_item_data.to_dict()
                footprints.append(footprints_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "workspace_id": workspace_id,
            }
        )
        if reviews is not UNSET:
            field_dict["reviews"] = reviews
        if automations is not UNSET:
            field_dict["automations"] = automations
        if footprints is not UNSET:
            field_dict["footprints"] = footprints

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.automation_run import AutomationRun  # noqa: PLC0415
        from ..models.footprint_day import FootprintDay  # noqa: PLC0415
        from ..models.review_day import ReviewDay  # noqa: PLC0415

        d = dict(src_dict)
        workspace_id = d.pop("workspace_id")

        _reviews = d.pop("reviews", UNSET)
        reviews: list[ReviewDay] | Unset = UNSET
        if _reviews is not UNSET:
            reviews = []
            for reviews_item_data in _reviews:
                reviews_item = ReviewDay.from_dict(reviews_item_data)

                reviews.append(reviews_item)

        _automations = d.pop("automations", UNSET)
        automations: list[AutomationRun] | Unset = UNSET
        if _automations is not UNSET:
            automations = []
            for automations_item_data in _automations:
                automations_item = AutomationRun.from_dict(automations_item_data)

                automations.append(automations_item)

        _footprints = d.pop("footprints", UNSET)
        footprints: list[FootprintDay] | Unset = UNSET
        if _footprints is not UNSET:
            footprints = []
            for footprints_item_data in _footprints:
                footprints_item = FootprintDay.from_dict(footprints_item_data)

                footprints.append(footprints_item)

        calendar_layers = cls(
            workspace_id=workspace_id,
            reviews=reviews,
            automations=automations,
            footprints=footprints,
        )

        calendar_layers.additional_properties = d
        return calendar_layers

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
