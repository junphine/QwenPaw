from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.channel_onboarding_start_request_channel import (
    ChannelOnboardingStartRequestChannel,
    check_channel_onboarding_start_request_channel,
)

T = TypeVar("T", bound="ChannelOnboardingStartRequest")


@_attrs_define
class ChannelOnboardingStartRequest:
    """
    Attributes:
        channel (ChannelOnboardingStartRequestChannel):
    """

    channel: ChannelOnboardingStartRequestChannel
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        channel: str = self.channel

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "channel": channel,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        channel = check_channel_onboarding_start_request_channel(d.pop("channel"))

        channel_onboarding_start_request = cls(
            channel=channel,
        )

        channel_onboarding_start_request.additional_properties = d
        return channel_onboarding_start_request

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
