from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PartnerGroupMessageRequest")


@_attrs_define
class PartnerGroupMessageRequest:
    """
    Attributes:
        content (str):
        session_key (str | Unset):  Default: 'default'.
        mentions (list[str] | None | Unset):
    """

    content: str
    session_key: str | Unset = "default"
    mentions: list[str] | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        content = self.content

        session_key = self.session_key

        mentions: list[str] | None | Unset
        if isinstance(self.mentions, Unset):
            mentions = UNSET
        elif isinstance(self.mentions, list):
            mentions = self.mentions

        else:
            mentions = self.mentions

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "content": content,
            }
        )
        if session_key is not UNSET:
            field_dict["session_key"] = session_key
        if mentions is not UNSET:
            field_dict["mentions"] = mentions

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        content = d.pop("content")

        session_key = d.pop("session_key", UNSET)

        def _parse_mentions(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                mentions_type_0 = cast(list[str], data)

                return mentions_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        mentions = _parse_mentions(d.pop("mentions", UNSET))

        partner_group_message_request = cls(
            content=content,
            session_key=session_key,
            mentions=mentions,
        )

        partner_group_message_request.additional_properties = d
        return partner_group_message_request

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
