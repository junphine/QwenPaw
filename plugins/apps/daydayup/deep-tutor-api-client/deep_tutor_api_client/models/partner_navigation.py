from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.navigation_session import NavigationSession
    from ..models.partner_navigation_groups_item import PartnerNavigationGroupsItem
    from ..models.partner_navigation_partners_item import PartnerNavigationPartnersItem


T = TypeVar("T", bound="PartnerNavigation")


@_attrs_define
class PartnerNavigation:
    """
    Attributes:
        partners (list[PartnerNavigationPartnersItem]):
        groups (list[PartnerNavigationGroupsItem]):
        sessions (list[NavigationSession]):
        unavailable (list[str]):
    """

    partners: list[PartnerNavigationPartnersItem]
    groups: list[PartnerNavigationGroupsItem]
    sessions: list[NavigationSession]
    unavailable: list[str]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        partners = []
        for partners_item_data in self.partners:
            partners_item = partners_item_data.to_dict()
            partners.append(partners_item)

        groups = []
        for groups_item_data in self.groups:
            groups_item = groups_item_data.to_dict()
            groups.append(groups_item)

        sessions = []
        for sessions_item_data in self.sessions:
            sessions_item = sessions_item_data.to_dict()
            sessions.append(sessions_item)

        unavailable = self.unavailable

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "partners": partners,
                "groups": groups,
                "sessions": sessions,
                "unavailable": unavailable,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.navigation_session import NavigationSession  # noqa: PLC0415
        from ..models.partner_navigation_groups_item import PartnerNavigationGroupsItem  # noqa: PLC0415
        from ..models.partner_navigation_partners_item import PartnerNavigationPartnersItem  # noqa: PLC0415

        d = dict(src_dict)
        partners = []
        _partners = d.pop("partners")
        for partners_item_data in _partners:
            partners_item = PartnerNavigationPartnersItem.from_dict(partners_item_data)

            partners.append(partners_item)

        groups = []
        _groups = d.pop("groups")
        for groups_item_data in _groups:
            groups_item = PartnerNavigationGroupsItem.from_dict(groups_item_data)

            groups.append(groups_item)

        sessions = []
        _sessions = d.pop("sessions")
        for sessions_item_data in _sessions:
            sessions_item = NavigationSession.from_dict(sessions_item_data)

            sessions.append(sessions_item)

        unavailable = cast(list[str], d.pop("unavailable"))

        partner_navigation = cls(
            partners=partners,
            groups=groups,
            sessions=sessions,
            unavailable=unavailable,
        )

        partner_navigation.additional_properties = d
        return partner_navigation

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
