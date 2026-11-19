from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.invidious_settings import InvidiousSettings
    from ..models.you_tube_settings import YouTubeSettings


T = TypeVar("T", bound="VideoLearningSettingsRequest")


@_attrs_define
class VideoLearningSettingsRequest:
    """
    Attributes:
        version (int | Unset):  Default: 1.
        default_provider (str | Unset):  Default: 'youtube'.
        youtube (YouTubeSettings | Unset):
        invidious (InvidiousSettings | Unset):
    """

    version: int | Unset = 1
    default_provider: str | Unset = "youtube"
    youtube: YouTubeSettings | Unset = UNSET
    invidious: InvidiousSettings | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        version = self.version

        default_provider = self.default_provider

        youtube: dict[str, Any] | Unset = UNSET
        if not isinstance(self.youtube, Unset):
            youtube = self.youtube.to_dict()

        invidious: dict[str, Any] | Unset = UNSET
        if not isinstance(self.invidious, Unset):
            invidious = self.invidious.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if version is not UNSET:
            field_dict["version"] = version
        if default_provider is not UNSET:
            field_dict["default_provider"] = default_provider
        if youtube is not UNSET:
            field_dict["youtube"] = youtube
        if invidious is not UNSET:
            field_dict["invidious"] = invidious

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.invidious_settings import InvidiousSettings  # noqa: PLC0415
        from ..models.you_tube_settings import YouTubeSettings  # noqa: PLC0415

        d = dict(src_dict)
        version = d.pop("version", UNSET)

        default_provider = d.pop("default_provider", UNSET)

        _youtube = d.pop("youtube", UNSET)
        youtube: YouTubeSettings | Unset
        if isinstance(_youtube, Unset):
            youtube = UNSET
        else:
            youtube = YouTubeSettings.from_dict(_youtube)

        _invidious = d.pop("invidious", UNSET)
        invidious: InvidiousSettings | Unset
        if isinstance(_invidious, Unset):
            invidious = UNSET
        else:
            invidious = InvidiousSettings.from_dict(_invidious)

        video_learning_settings_request = cls(
            version=version,
            default_provider=default_provider,
            youtube=youtube,
            invidious=invidious,
        )

        video_learning_settings_request.additional_properties = d
        return video_learning_settings_request

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
