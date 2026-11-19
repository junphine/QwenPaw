from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.display_settings_content_font_scale import (
    DisplaySettingsContentFontScale,
    check_display_settings_content_font_scale,
)
from ..models.display_settings_content_line_spacing import (
    DisplaySettingsContentLineSpacing,
    check_display_settings_content_line_spacing,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="DisplaySettings")


@_attrs_define
class DisplaySettings:
    """Account-scoped learning text preferences; no interface chrome settings.

    Attributes:
        content_font_scale (DisplaySettingsContentFontScale | Unset):  Default: 100.
        content_line_spacing (DisplaySettingsContentLineSpacing | Unset):  Default: 'normal'.
    """

    content_font_scale: DisplaySettingsContentFontScale | Unset = 100
    content_line_spacing: DisplaySettingsContentLineSpacing | Unset = "normal"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        content_font_scale: int | Unset = UNSET
        if not isinstance(self.content_font_scale, Unset):
            content_font_scale = self.content_font_scale

        content_line_spacing: str | Unset = UNSET
        if not isinstance(self.content_line_spacing, Unset):
            content_line_spacing = self.content_line_spacing

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if content_font_scale is not UNSET:
            field_dict["content_font_scale"] = content_font_scale
        if content_line_spacing is not UNSET:
            field_dict["content_line_spacing"] = content_line_spacing

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        _content_font_scale = d.pop("content_font_scale", UNSET)
        content_font_scale: DisplaySettingsContentFontScale | Unset
        if isinstance(_content_font_scale, Unset):
            content_font_scale = UNSET
        else:
            content_font_scale = check_display_settings_content_font_scale(_content_font_scale)

        _content_line_spacing = d.pop("content_line_spacing", UNSET)
        content_line_spacing: DisplaySettingsContentLineSpacing | Unset
        if isinstance(_content_line_spacing, Unset):
            content_line_spacing = UNSET
        else:
            content_line_spacing = check_display_settings_content_line_spacing(_content_line_spacing)

        display_settings = cls(
            content_font_scale=content_font_scale,
            content_line_spacing=content_line_spacing,
        )

        display_settings.additional_properties = d
        return display_settings

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
