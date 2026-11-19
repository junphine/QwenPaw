from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.update_partner_request_backup_llm_selection_type_0 import UpdatePartnerRequestBackupLlmSelectionType0
    from ..models.update_partner_request_channels_type_0 import UpdatePartnerRequestChannelsType0
    from ..models.update_partner_request_llm_selection_type_0 import UpdatePartnerRequestLlmSelectionType0


T = TypeVar("T", bound="UpdatePartnerRequest")


@_attrs_define
class UpdatePartnerRequest:
    """
    Attributes:
        workspace_id (None | str | Unset):
        name (None | str | Unset):
        description (None | str | Unset):
        channels (None | Unset | UpdatePartnerRequestChannelsType0):
        llm_selection (None | Unset | UpdatePartnerRequestLlmSelectionType0):
        backup_llm_selection (None | Unset | UpdatePartnerRequestBackupLlmSelectionType0):
        language (None | str | Unset):
        emoji (None | str | Unset):
        color (None | str | Unset):
        avatar (None | str | Unset):
        enabled_tools (list[str] | None | Unset):
        builtin_tools (list[str] | None | Unset):
        mcp_tools (list[str] | None | Unset):
    """

    workspace_id: None | str | Unset = UNSET
    name: None | str | Unset = UNSET
    description: None | str | Unset = UNSET
    channels: None | Unset | UpdatePartnerRequestChannelsType0 = UNSET
    llm_selection: None | Unset | UpdatePartnerRequestLlmSelectionType0 = UNSET
    backup_llm_selection: None | Unset | UpdatePartnerRequestBackupLlmSelectionType0 = UNSET
    language: None | str | Unset = UNSET
    emoji: None | str | Unset = UNSET
    color: None | str | Unset = UNSET
    avatar: None | str | Unset = UNSET
    enabled_tools: list[str] | None | Unset = UNSET
    builtin_tools: list[str] | None | Unset = UNSET
    mcp_tools: list[str] | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.update_partner_request_backup_llm_selection_type_0 import (
            UpdatePartnerRequestBackupLlmSelectionType0,  # noqa: PLC0415
        )
        from ..models.update_partner_request_channels_type_0 import UpdatePartnerRequestChannelsType0  # noqa: PLC0415
        from ..models.update_partner_request_llm_selection_type_0 import (
            UpdatePartnerRequestLlmSelectionType0,  # noqa: PLC0415
        )

        workspace_id: None | str | Unset
        if isinstance(self.workspace_id, Unset):
            workspace_id = UNSET
        else:
            workspace_id = self.workspace_id

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

        channels: dict[str, Any] | None | Unset
        if isinstance(self.channels, Unset):
            channels = UNSET
        elif isinstance(self.channels, UpdatePartnerRequestChannelsType0):
            channels = self.channels.to_dict()
        else:
            channels = self.channels

        llm_selection: dict[str, Any] | None | Unset
        if isinstance(self.llm_selection, Unset):
            llm_selection = UNSET
        elif isinstance(self.llm_selection, UpdatePartnerRequestLlmSelectionType0):
            llm_selection = self.llm_selection.to_dict()
        else:
            llm_selection = self.llm_selection

        backup_llm_selection: dict[str, Any] | None | Unset
        if isinstance(self.backup_llm_selection, Unset):
            backup_llm_selection = UNSET
        elif isinstance(self.backup_llm_selection, UpdatePartnerRequestBackupLlmSelectionType0):
            backup_llm_selection = self.backup_llm_selection.to_dict()
        else:
            backup_llm_selection = self.backup_llm_selection

        language: None | str | Unset
        if isinstance(self.language, Unset):
            language = UNSET
        else:
            language = self.language

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

        avatar: None | str | Unset
        if isinstance(self.avatar, Unset):
            avatar = UNSET
        else:
            avatar = self.avatar

        enabled_tools: list[str] | None | Unset
        if isinstance(self.enabled_tools, Unset):
            enabled_tools = UNSET
        elif isinstance(self.enabled_tools, list):
            enabled_tools = self.enabled_tools

        else:
            enabled_tools = self.enabled_tools

        builtin_tools: list[str] | None | Unset
        if isinstance(self.builtin_tools, Unset):
            builtin_tools = UNSET
        elif isinstance(self.builtin_tools, list):
            builtin_tools = self.builtin_tools

        else:
            builtin_tools = self.builtin_tools

        mcp_tools: list[str] | None | Unset
        if isinstance(self.mcp_tools, Unset):
            mcp_tools = UNSET
        elif isinstance(self.mcp_tools, list):
            mcp_tools = self.mcp_tools

        else:
            mcp_tools = self.mcp_tools

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if workspace_id is not UNSET:
            field_dict["workspace_id"] = workspace_id
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description
        if channels is not UNSET:
            field_dict["channels"] = channels
        if llm_selection is not UNSET:
            field_dict["llm_selection"] = llm_selection
        if backup_llm_selection is not UNSET:
            field_dict["backup_llm_selection"] = backup_llm_selection
        if language is not UNSET:
            field_dict["language"] = language
        if emoji is not UNSET:
            field_dict["emoji"] = emoji
        if color is not UNSET:
            field_dict["color"] = color
        if avatar is not UNSET:
            field_dict["avatar"] = avatar
        if enabled_tools is not UNSET:
            field_dict["enabled_tools"] = enabled_tools
        if builtin_tools is not UNSET:
            field_dict["builtin_tools"] = builtin_tools
        if mcp_tools is not UNSET:
            field_dict["mcp_tools"] = mcp_tools

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.update_partner_request_backup_llm_selection_type_0 import (
            UpdatePartnerRequestBackupLlmSelectionType0,  # noqa: PLC0415
        )
        from ..models.update_partner_request_channels_type_0 import UpdatePartnerRequestChannelsType0  # noqa: PLC0415
        from ..models.update_partner_request_llm_selection_type_0 import (
            UpdatePartnerRequestLlmSelectionType0,  # noqa: PLC0415
        )

        d = dict(src_dict)

        def _parse_workspace_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        workspace_id = _parse_workspace_id(d.pop("workspace_id", UNSET))

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

        def _parse_channels(data: object) -> None | Unset | UpdatePartnerRequestChannelsType0:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                channels_type_0 = UpdatePartnerRequestChannelsType0.from_dict(data)

                return channels_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UpdatePartnerRequestChannelsType0, data)

        channels = _parse_channels(d.pop("channels", UNSET))

        def _parse_llm_selection(data: object) -> None | Unset | UpdatePartnerRequestLlmSelectionType0:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                llm_selection_type_0 = UpdatePartnerRequestLlmSelectionType0.from_dict(data)

                return llm_selection_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UpdatePartnerRequestLlmSelectionType0, data)

        llm_selection = _parse_llm_selection(d.pop("llm_selection", UNSET))

        def _parse_backup_llm_selection(data: object) -> None | Unset | UpdatePartnerRequestBackupLlmSelectionType0:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                backup_llm_selection_type_0 = UpdatePartnerRequestBackupLlmSelectionType0.from_dict(data)

                return backup_llm_selection_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UpdatePartnerRequestBackupLlmSelectionType0, data)

        backup_llm_selection = _parse_backup_llm_selection(d.pop("backup_llm_selection", UNSET))

        def _parse_language(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        language = _parse_language(d.pop("language", UNSET))

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

        def _parse_avatar(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        avatar = _parse_avatar(d.pop("avatar", UNSET))

        def _parse_enabled_tools(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                enabled_tools_type_0 = cast(list[str], data)

                return enabled_tools_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        enabled_tools = _parse_enabled_tools(d.pop("enabled_tools", UNSET))

        def _parse_builtin_tools(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                builtin_tools_type_0 = cast(list[str], data)

                return builtin_tools_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        builtin_tools = _parse_builtin_tools(d.pop("builtin_tools", UNSET))

        def _parse_mcp_tools(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                mcp_tools_type_0 = cast(list[str], data)

                return mcp_tools_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        mcp_tools = _parse_mcp_tools(d.pop("mcp_tools", UNSET))

        update_partner_request = cls(
            workspace_id=workspace_id,
            name=name,
            description=description,
            channels=channels,
            llm_selection=llm_selection,
            backup_llm_selection=backup_llm_selection,
            language=language,
            emoji=emoji,
            color=color,
            avatar=avatar,
            enabled_tools=enabled_tools,
            builtin_tools=builtin_tools,
            mcp_tools=mcp_tools,
        )

        update_partner_request.additional_properties = d
        return update_partner_request

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
