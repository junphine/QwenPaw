from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.knowledge_point_input import KnowledgePointInput


T = TypeVar("T", bound="ModuleInput")


@_attrs_define
class ModuleInput:
    """
    Attributes:
        name (str):
        id (None | str | Unset):
        order (int | None | Unset):
        objective (str | Unset):  Default: ''.
        pass_threshold (float | Unset):  Default: 0.7.
        knowledge_points (list[KnowledgePointInput] | Unset):
    """

    name: str
    id: None | str | Unset = UNSET
    order: int | None | Unset = UNSET
    objective: str | Unset = ""
    pass_threshold: float | Unset = 0.7
    knowledge_points: list[KnowledgePointInput] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        id: None | str | Unset
        if isinstance(self.id, Unset):
            id = UNSET
        else:
            id = self.id

        order: int | None | Unset
        if isinstance(self.order, Unset):
            order = UNSET
        else:
            order = self.order

        objective = self.objective

        pass_threshold = self.pass_threshold

        knowledge_points: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.knowledge_points, Unset):
            knowledge_points = []
            for knowledge_points_item_data in self.knowledge_points:
                knowledge_points_item = knowledge_points_item_data.to_dict()
                knowledge_points.append(knowledge_points_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
            }
        )
        if id is not UNSET:
            field_dict["id"] = id
        if order is not UNSET:
            field_dict["order"] = order
        if objective is not UNSET:
            field_dict["objective"] = objective
        if pass_threshold is not UNSET:
            field_dict["pass_threshold"] = pass_threshold
        if knowledge_points is not UNSET:
            field_dict["knowledge_points"] = knowledge_points

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.knowledge_point_input import KnowledgePointInput  # noqa: PLC0415

        d = dict(src_dict)
        name = d.pop("name")

        def _parse_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        id = _parse_id(d.pop("id", UNSET))

        def _parse_order(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        order = _parse_order(d.pop("order", UNSET))

        objective = d.pop("objective", UNSET)

        pass_threshold = d.pop("pass_threshold", UNSET)

        _knowledge_points = d.pop("knowledge_points", UNSET)
        knowledge_points: list[KnowledgePointInput] | Unset = UNSET
        if _knowledge_points is not UNSET:
            knowledge_points = []
            for knowledge_points_item_data in _knowledge_points:
                knowledge_points_item = KnowledgePointInput.from_dict(knowledge_points_item_data)

                knowledge_points.append(knowledge_points_item)

        module_input = cls(
            name=name,
            id=id,
            order=order,
            objective=objective,
            pass_threshold=pass_threshold,
            knowledge_points=knowledge_points,
        )

        module_input.additional_properties = d
        return module_input

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
