from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.navigation_session_kind import NavigationSessionKind, check_navigation_session_kind

T = TypeVar("T", bound="NavigationSession")


@_attrs_define
class NavigationSession:
    """
    Attributes:
        kind (NavigationSessionKind):
        owner_id (str):
        owner_name (str):
        session_key (str):
        title (str):
        updated_at (float):
    """

    kind: NavigationSessionKind
    owner_id: str
    owner_name: str
    session_key: str
    title: str
    updated_at: float
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        kind: str = self.kind

        owner_id = self.owner_id

        owner_name = self.owner_name

        session_key = self.session_key

        title = self.title

        updated_at = self.updated_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "kind": kind,
                "owner_id": owner_id,
                "owner_name": owner_name,
                "session_key": session_key,
                "title": title,
                "updated_at": updated_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        kind = check_navigation_session_kind(d.pop("kind"))

        owner_id = d.pop("owner_id")

        owner_name = d.pop("owner_name")

        session_key = d.pop("session_key")

        title = d.pop("title")

        updated_at = d.pop("updated_at")

        navigation_session = cls(
            kind=kind,
            owner_id=owner_id,
            owner_name=owner_name,
            session_key=session_key,
            title=title,
            updated_at=updated_at,
        )

        navigation_session.additional_properties = d
        return navigation_session

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
