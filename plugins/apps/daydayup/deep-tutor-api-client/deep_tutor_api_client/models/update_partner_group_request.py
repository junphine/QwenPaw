from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="UpdatePartnerGroupRequest")


@_attrs_define
class UpdatePartnerGroupRequest:
    """
    Attributes:
        name (None | str | Unset):
        description (None | str | Unset):
        member_ids (list[str] | None | Unset):
        discussion_mode (None | str | Unset):
        shared_memory (None | str | Unset):
        emoji (None | str | Unset):
        color (None | str | Unset):
    """

    name: None | str | Unset = UNSET
    description: None | str | Unset = UNSET
    member_ids: list[str] | None | Unset = UNSET
    discussion_mode: None | str | Unset = UNSET
    shared_memory: None | str | Unset = UNSET
    emoji: None | str | Unset = UNSET
    color: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name: None | str | Unset
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        member_ids: list[str] | None | Unset
        if isinstance(self.member_ids, Unset):
            member_ids = UNSET
        elif isinstance(self.member_ids, list):
            member_ids = self.member_ids

        else:
            member_ids = self.member_ids

        discussion_mode: None | str | Unset
        if isinstance(self.discussion_mode, Unset):
            discussion_mode = UNSET
        else:
            discussion_mode = self.discussion_mode

        shared_memory: None | str | Unset
        if isinstance(self.shared_memory, Unset):
            shared_memory = UNSET
        else:
            shared_memory = self.shared_memory

        emoji: None | str | Unset
        if isinstance(self.emoji, Unset):
            emoji = UNSET
        else:
            emoji = self.emoji

        color: None | str | Unset
        if isinstance(self.color, Unset):
            color = UNSET
        else:
            color = self.color

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description
        if member_ids is not UNSET:
            field_dict["member_ids"] = member_ids
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

        def _parse_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        name = _parse_name(d.pop("name", UNSET))

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_member_ids(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                member_ids_type_0 = cast(list[str], data)

                return member_ids_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        member_ids = _parse_member_ids(d.pop("member_ids", UNSET))

        def _parse_discussion_mode(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        discussion_mode = _parse_discussion_mode(d.pop("discussion_mode", UNSET))

        def _parse_shared_memory(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        shared_memory = _parse_shared_memory(d.pop("shared_memory", UNSET))

        def _parse_emoji(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        emoji = _parse_emoji(d.pop("emoji", UNSET))

        def _parse_color(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        color = _parse_color(d.pop("color", UNSET))

        update_partner_group_request = cls(
            name=name,
            description=description,
            member_ids=member_ids,
            discussion_mode=discussion_mode,
            shared_memory=shared_memory,
            emoji=emoji,
            color=color,
        )

        update_partner_group_request.additional_properties = d
        return update_partner_group_request

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
