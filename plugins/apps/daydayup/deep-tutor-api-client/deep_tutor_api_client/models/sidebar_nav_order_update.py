from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.sidebar_nav_order import SidebarNavOrder


T = TypeVar("T", bound="SidebarNavOrderUpdate")


@_attrs_define
class SidebarNavOrderUpdate:
    """
    Attributes:
        nav_order (SidebarNavOrder):
    """

    nav_order: SidebarNavOrder
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        nav_order = self.nav_order.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "nav_order": nav_order,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.sidebar_nav_order import SidebarNavOrder  # noqa: PLC0415

        d = dict(src_dict)
        nav_order = SidebarNavOrder.from_dict(d.pop("nav_order"))

        sidebar_nav_order_update = cls(
            nav_order=nav_order,
        )

        sidebar_nav_order_update.additional_properties = d
        return sidebar_nav_order_update

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
