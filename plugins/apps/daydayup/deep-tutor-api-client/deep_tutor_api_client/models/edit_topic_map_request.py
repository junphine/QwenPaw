from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.module_input import ModuleInput


T = TypeVar("T", bound="EditTopicMapRequest")


@_attrs_define
class EditTopicMapRequest:
    """
    Attributes:
        modules (list[ModuleInput]):
    """

    modules: list[ModuleInput]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        modules = []
        for modules_item_data in self.modules:
            modules_item = modules_item_data.to_dict()
            modules.append(modules_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "modules": modules,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.module_input import ModuleInput  # noqa: PLC0415

        d = dict(src_dict)
        modules = []
        _modules = d.pop("modules")
        for modules_item_data in _modules:
            modules_item = ModuleInput.from_dict(modules_item_data)

            modules.append(modules_item)

        edit_topic_map_request = cls(
            modules=modules,
        )

        edit_topic_map_request.additional_properties = d
        return edit_topic_map_request

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
