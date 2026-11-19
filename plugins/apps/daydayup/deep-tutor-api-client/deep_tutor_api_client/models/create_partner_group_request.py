from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="CreatePartnerGroupRequest")


@_attrs_define
class CreatePartnerGroupRequest:
    """
    Attributes:
        name (str):
        member_ids (list[str]):
        description (str | Unset):  Default: ''.
        discussion_mode (str | Unset):  Default: 'panel_parallel'.
        shared_memory (str | Unset):  Default: 'whiteboard'.
        emoji (str | Unset):  Default: '👥'.
        color (str | Unset):  Default: '#6366f1'.
    """

    name: str
    member_ids: list[str]
    description: str | Unset = ""
    discussion_mode: str | Unset = "panel_parallel"
    shared_memory: str | Unset = "whiteboard"
    emoji: str | Unset = "👥"
    color: str | Unset = "#6366f1"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        member_ids = self.member_ids

        description = self.description

        discussion_mode = self.discussion_mode

        shared_memory = self.shared_memory

        emoji = self.emoji

        color = self.color

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "member_ids": member_ids,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if discussion_mode is not UNSET:
            field_dict["discussion_mode"] = discussion_mode
        if shared_memory is not UNSET:
            field_dict["shared_memory"] = shared_memory
        if emoji is not UNSET:
            field_dict["emoji"] = emoji
        if color is not UNSET:
            field_dict["color"] = color

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        member_ids = cast(list[str], d.pop("member_ids"))

        description = d.pop("description", UNSET)

        discussion_mode = d.pop("discussion_mode", UNSET)

        shared_memory = d.pop("shared_memory", UNSET)

        emoji = d.pop("emoji", UNSET)

        color = d.pop("color", UNSET)

        create_partner_group_request = cls(
            name=name,
            member_ids=member_ids,
            description=description,
            discussion_mode=discussion_mode,
            shared_memory=shared_memory,
            emoji=emoji,
            color=color,
        )

        create_partner_group_request.additional_properties = d
        return create_partner_group_request

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
