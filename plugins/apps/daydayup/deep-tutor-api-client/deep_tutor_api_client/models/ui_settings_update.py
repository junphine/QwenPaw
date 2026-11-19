from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.ui_settings_update_content_font_scale import (
    UISettingsUpdateContentFontScale,
    check_ui_settings_update_content_font_scale,
)
from ..models.ui_settings_update_content_line_spacing import (
    UISettingsUpdateContentLineSpacing,
    check_ui_settings_update_content_line_spacing,
)
from ..models.ui_settings_update_language_type_0 import (
    UISettingsUpdateLanguageType0,
    check_ui_settings_update_language_type_0,
)
from ..models.ui_settings_update_response_language_type_0 import (
    UISettingsUpdateResponseLanguageType0,
    check_ui_settings_update_response_language_type_0,
)
from ..models.ui_settings_update_theme_type_0 import UISettingsUpdateThemeType0, check_ui_settings_update_theme_type_0
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.sidebar_nav_order import SidebarNavOrder


T = TypeVar("T", bound="UISettingsUpdate")


@_attrs_define
class UISettingsUpdate:
    """Partial UI settings for user-initiated PATCH/PUT updates via /api/settings/ui.

    `model_dump(exclude_unset=True)` excludes fields not provided in the
    frontend payload, while explicitly provided
    defaults (e.g., `theme: "snow"`) still update the backend. This separates
    the semantic contract: `/ui` endpoint only merges whatever explicitly arrives
    from the frontend.

        Attributes:
            content_font_scale (UISettingsUpdateContentFontScale | Unset):  Default: 100.
            content_line_spacing (UISettingsUpdateContentLineSpacing | Unset):  Default: 'normal'.
            theme (None | UISettingsUpdateThemeType0 | Unset):
            language (None | UISettingsUpdateLanguageType0 | Unset):
            response_language (None | UISettingsUpdateResponseLanguageType0 | Unset):
            sidebar_description (None | str | Unset):
            sidebar_nav_order (None | SidebarNavOrder | Unset):
            code_block_theme (None | str | Unset):
            code_block_show_line_numbers (bool | None | Unset):
            code_block_wrap_long_lines (bool | None | Unset):
    """

    content_font_scale: UISettingsUpdateContentFontScale | Unset = 100
    content_line_spacing: UISettingsUpdateContentLineSpacing | Unset = "normal"
    theme: None | UISettingsUpdateThemeType0 | Unset = UNSET
    language: None | UISettingsUpdateLanguageType0 | Unset = UNSET
    response_language: None | UISettingsUpdateResponseLanguageType0 | Unset = UNSET
    sidebar_description: None | str | Unset = UNSET
    sidebar_nav_order: None | SidebarNavOrder | Unset = UNSET
    code_block_theme: None | str | Unset = UNSET
    code_block_show_line_numbers: bool | None | Unset = UNSET
    code_block_wrap_long_lines: bool | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.sidebar_nav_order import SidebarNavOrder  # noqa: PLC0415

        content_font_scale: int | Unset = UNSET
        if not isinstance(self.content_font_scale, Unset):
            content_font_scale = self.content_font_scale

        content_line_spacing: str | Unset = UNSET
        if not isinstance(self.content_line_spacing, Unset):
            content_line_spacing = self.content_line_spacing

        theme: None | str | Unset
        if isinstance(self.theme, Unset):
            theme = UNSET
        elif isinstance(self.theme, str):
            theme = self.theme
        else:
            theme = self.theme

        language: None | str | Unset
        if isinstance(self.language, Unset):
            language = UNSET
        elif isinstance(self.language, str):
            language = self.language
        else:
            language = self.language

        response_language: None | str | Unset
        if isinstance(self.response_language, Unset):
            response_language = UNSET
        elif isinstance(self.response_language, str):
            response_language = self.response_language
        else:
            response_language = self.response_language

        sidebar_description: None | str | Unset
        if isinstance(self.sidebar_description, Unset):
            sidebar_description = UNSET
        else:
            sidebar_description = self.sidebar_description

        sidebar_nav_order: dict[str, Any] | None | Unset
        if isinstance(self.sidebar_nav_order, Unset):
            sidebar_nav_order = UNSET
        elif isinstance(self.sidebar_nav_order, SidebarNavOrder):
            sidebar_nav_order = self.sidebar_nav_order.to_dict()
        else:
            sidebar_nav_order = self.sidebar_nav_order

        code_block_theme: None | str | Unset
        if isinstance(self.code_block_theme, Unset):
            code_block_theme = UNSET
        else:
            code_block_theme = self.code_block_theme

        code_block_show_line_numbers: bool | None | Unset
        if isinstance(self.code_block_show_line_numbers, Unset):
            code_block_show_line_numbers = UNSET
        else:
            code_block_show_line_numbers = self.code_block_show_line_numbers

        code_block_wrap_long_lines: bool | None | Unset
        if isinstance(self.code_block_wrap_long_lines, Unset):
            code_block_wrap_long_lines = UNSET
        else:
            code_block_wrap_long_lines = self.code_block_wrap_long_lines

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if content_font_scale is not UNSET:
            field_dict["content_font_scale"] = content_font_scale
        if content_line_spacing is not UNSET:
            field_dict["content_line_spacing"] = content_line_spacing
        if theme is not UNSET:
            field_dict["theme"] = theme
        if language is not UNSET:
            field_dict["language"] = language
        if response_language is not UNSET:
            field_dict["response_language"] = response_language
        if sidebar_description is not UNSET:
            field_dict["sidebar_description"] = sidebar_description
        if sidebar_nav_order is not UNSET:
            field_dict["sidebar_nav_order"] = sidebar_nav_order
        if code_block_theme is not UNSET:
            field_dict["code_block_theme"] = code_block_theme
        if code_block_show_line_numbers is not UNSET:
            field_dict["code_block_show_line_numbers"] = code_block_show_line_numbers
        if code_block_wrap_long_lines is not UNSET:
            field_dict["code_block_wrap_long_lines"] = code_block_wrap_long_lines

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.sidebar_nav_order import SidebarNavOrder  # noqa: PLC0415

        d = dict(src_dict)
        _content_font_scale = d.pop("content_font_scale", UNSET)
        content_font_scale: UISettingsUpdateContentFontScale | Unset
        if isinstance(_content_font_scale, Unset):
            content_font_scale = UNSET
        else:
            content_font_scale = check_ui_settings_update_content_font_scale(_content_font_scale)

        _content_line_spacing = d.pop("content_line_spacing", UNSET)
        content_line_spacing: UISettingsUpdateContentLineSpacing | Unset
        if isinstance(_content_line_spacing, Unset):
            content_line_spacing = UNSET
        else:
            content_line_spacing = check_ui_settings_update_content_line_spacing(_content_line_spacing)

        def _parse_theme(data: object) -> None | UISettingsUpdateThemeType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                theme_type_0 = check_ui_settings_update_theme_type_0(data)

                return theme_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | UISettingsUpdateThemeType0 | Unset, data)

        theme = _parse_theme(d.pop("theme", UNSET))

        def _parse_language(data: object) -> None | UISettingsUpdateLanguageType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                language_type_0 = check_ui_settings_update_language_type_0(data)

                return language_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | UISettingsUpdateLanguageType0 | Unset, data)

        language = _parse_language(d.pop("language", UNSET))

        def _parse_response_language(data: object) -> None | UISettingsUpdateResponseLanguageType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                response_language_type_0 = check_ui_settings_update_response_language_type_0(data)

                return response_language_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | UISettingsUpdateResponseLanguageType0 | Unset, data)

        response_language = _parse_response_language(d.pop("response_language", UNSET))

        def _parse_sidebar_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        sidebar_description = _parse_sidebar_description(d.pop("sidebar_description", UNSET))

        def _parse_sidebar_nav_order(data: object) -> None | SidebarNavOrder | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                sidebar_nav_order_type_0 = SidebarNavOrder.from_dict(data)

                return sidebar_nav_order_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | SidebarNavOrder | Unset, data)

        sidebar_nav_order = _parse_sidebar_nav_order(d.pop("sidebar_nav_order", UNSET))

        def _parse_code_block_theme(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        code_block_theme = _parse_code_block_theme(d.pop("code_block_theme", UNSET))

        def _parse_code_block_show_line_numbers(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        code_block_show_line_numbers = _parse_code_block_show_line_numbers(d.pop("code_block_show_line_numbers", UNSET))

        def _parse_code_block_wrap_long_lines(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        code_block_wrap_long_lines = _parse_code_block_wrap_long_lines(d.pop("code_block_wrap_long_lines", UNSET))

        ui_settings_update = cls(
            content_font_scale=content_font_scale,
            content_line_spacing=content_line_spacing,
            theme=theme,
            language=language,
            response_language=response_language,
            sidebar_description=sidebar_description,
            sidebar_nav_order=sidebar_nav_order,
            code_block_theme=code_block_theme,
            code_block_show_line_numbers=code_block_show_line_numbers,
            code_block_wrap_long_lines=code_block_wrap_long_lines,
        )

        ui_settings_update.additional_properties = d
        return ui_settings_update

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
