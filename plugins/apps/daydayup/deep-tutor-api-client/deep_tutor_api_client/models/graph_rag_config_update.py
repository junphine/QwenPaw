from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GraphRagConfigUpdate")


@_attrs_define
class GraphRagConfigUpdate:
    """Partial update for GraphRAG query knobs (omitted fields kept).

    Attributes:
        response_type (None | str | Unset):
        community_level (int | None | Unset):
        dynamic_community_selection (bool | None | Unset):
    """

    response_type: None | str | Unset = UNSET
    community_level: int | None | Unset = UNSET
    dynamic_community_selection: bool | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        response_type: None | str | Unset
        if isinstance(self.response_type, Unset):
            response_type = UNSET
        else:
            response_type = self.response_type

        community_level: int | None | Unset
        if isinstance(self.community_level, Unset):
            community_level = UNSET
        else:
            community_level = self.community_level

        dynamic_community_selection: bool | None | Unset
        if isinstance(self.dynamic_community_selection, Unset):
            dynamic_community_selection = UNSET
        else:
            dynamic_community_selection = self.dynamic_community_selection

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if response_type is not UNSET:
            field_dict["response_type"] = response_type
        if community_level is not UNSET:
            field_dict["community_level"] = community_level
        if dynamic_community_selection is not UNSET:
            field_dict["dynamic_community_selection"] = dynamic_community_selection

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_response_type(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        response_type = _parse_response_type(d.pop("response_type", UNSET))

        def _parse_community_level(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        community_level = _parse_community_level(d.pop("community_level", UNSET))

        def _parse_dynamic_community_selection(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        dynamic_community_selection = _parse_dynamic_community_selection(d.pop("dynamic_community_selection", UNSET))

        graph_rag_config_update = cls(
            response_type=response_type,
            community_level=community_level,
            dynamic_community_selection=dynamic_community_selection,
        )

        graph_rag_config_update.additional_properties = d
        return graph_rag_config_update

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
