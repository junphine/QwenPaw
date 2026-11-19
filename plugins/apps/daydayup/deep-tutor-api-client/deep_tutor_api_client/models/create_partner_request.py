from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.asset_spec import AssetSpec
    from ..models.create_partner_request_backup_llm_selection_type_0 import CreatePartnerRequestBackupLlmSelectionType0
    from ..models.create_partner_request_channels_type_0 import CreatePartnerRequestChannelsType0
    from ..models.create_partner_request_llm_selection_type_0 import CreatePartnerRequestLlmSelectionType0
    from ..models.soul_spec import SoulSpec


T = TypeVar("T", bound="CreatePartnerRequest")


@_attrs_define
class CreatePartnerRequest:
    """
    Attributes:
        name (str):
        workspace_id (str | Unset):  Default: ''.
        partner_id (None | str | Unset):
        description (None | str | Unset):
        soul (None | SoulSpec | Unset):
        channels (CreatePartnerRequestChannelsType0 | None | Unset):
        llm_selection (CreatePartnerRequestLlmSelectionType0 | None | Unset):
        backup_llm_selection (CreatePartnerRequestBackupLlmSelectionType0 | None | Unset):
        language (None | str | Unset):
        emoji (None | str | Unset):
        color (None | str | Unset):
        avatar (None | str | Unset):
        enabled_tools (list[str] | None | Unset):
        builtin_tools (list[str] | None | Unset):
        mcp_tools (list[str] | None | Unset):
        assets (AssetSpec | None | Unset):
        start (bool | Unset):  Default: True.
    """

    name: str
    workspace_id: str | Unset = ""
    partner_id: None | str | Unset = UNSET
    description: None | str | Unset = UNSET
    soul: None | SoulSpec | Unset = UNSET
    channels: CreatePartnerRequestChannelsType0 | None | Unset = UNSET
    llm_selection: CreatePartnerRequestLlmSelectionType0 | None | Unset = UNSET
    backup_llm_selection: CreatePartnerRequestBackupLlmSelectionType0 | None | Unset = UNSET
    language: None | str | Unset = UNSET
    emoji: None | str | Unset = UNSET
    color: None | str | Unset = UNSET
    avatar: None | str | Unset = UNSET
    enabled_tools: list[str] | None | Unset = UNSET
    builtin_tools: list[str] | None | Unset = UNSET
    mcp_tools: list[str] | None | Unset = UNSET
    assets: AssetSpec | None | Unset = UNSET
    start: bool | Unset = True
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.asset_spec import AssetSpec  # noqa: PLC0415
        from ..models.create_partner_request_backup_llm_selection_type_0 import (
            CreatePartnerRequestBackupLlmSelectionType0,  # noqa: PLC0415
        )
        from ..models.create_partner_request_channels_type_0 import CreatePartnerRequestChannelsType0  # noqa: PLC0415
        from ..models.create_partner_request_llm_selection_type_0 import (
            CreatePartnerRequestLlmSelectionType0,  # noqa: PLC0415
        )
        from ..models.soul_spec import SoulSpec  # noqa: PLC0415

        name = self.name

        workspace_id = self.workspace_id

        partner_id: None | str | Unset
        if isinstance(self.partner_id, Unset):
            partner_id = UNSET
        else:
            partner_id = self.partner_id

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        soul: dict[str, Any] | None | Unset
        if isinstance(self.soul, Unset):
            soul = UNSET
        elif isinstance(self.soul, SoulSpec):
            soul = self.soul.to_dict()
        else:
            soul = self.soul

        channels: dict[str, Any] | None | Unset
        if isinstance(self.channels, Unset):
            channels = UNSET
        elif isinstance(self.channels, CreatePartnerRequestChannelsType0):
            channels = self.channels.to_dict()
        else:
            channels = self.channels

        llm_selection: dict[str, Any] | None | Unset
        if isinstance(self.llm_selection, Unset):
            llm_selection = UNSET
        elif isinstance(self.llm_selection, CreatePartnerRequestLlmSelectionType0):
            llm_selection = self.llm_selection.to_dict()
        else:
            llm_selection = self.llm_selection

        backup_llm_selection: dict[str, Any] | None | Unset
        if isinstance(self.backup_llm_selection, Unset):
            backup_llm_selection = UNSET
        elif isinstance(self.backup_llm_selection, CreatePartnerRequestBackupLlmSelectionType0):
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

        assets: dict[str, Any] | None | Unset
        if isinstance(self.assets, Unset):
            assets = UNSET
        elif isinstance(self.assets, AssetSpec):
            assets = self.assets.to_dict()
        else:
            assets = self.assets

        start = self.start

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
            }
        )
        if workspace_id is not UNSET:
            field_dict["workspace_id"] = workspace_id
        if partner_id is not UNSET:
            field_dict["partner_id"] = partner_id
        if description is not UNSET:
            field_dict["description"] = description
        if soul is not UNSET:
            field_dict["soul"] = soul
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
        if assets is not UNSET:
            field_dict["assets"] = assets
        if start is not UNSET:
            field_dict["start"] = start

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.asset_spec import AssetSpec  # noqa: PLC0415
        from ..models.create_partner_request_backup_llm_selection_type_0 import (
            CreatePartnerRequestBackupLlmSelectionType0,  # noqa: PLC0415
        )
        from ..models.create_partner_request_channels_type_0 import CreatePartnerRequestChannelsType0  # noqa: PLC0415
        from ..models.create_partner_request_llm_selection_type_0 import (
            CreatePartnerRequestLlmSelectionType0,  # noqa: PLC0415
        )
        from ..models.soul_spec import SoulSpec  # noqa: PLC0415

        d = dict(src_dict)
        name = d.pop("name")

        workspace_id = d.pop("workspace_id", UNSET)

        def _parse_partner_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        partner_id = _parse_partner_id(d.pop("partner_id", UNSET))

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_soul(data: object) -> None | SoulSpec | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                soul_type_0 = SoulSpec.from_dict(data)

                return soul_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | SoulSpec | Unset, data)

        soul = _parse_soul(d.pop("soul", UNSET))

        def _parse_channels(data: object) -> CreatePartnerRequestChannelsType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                channels_type_0 = CreatePartnerRequestChannelsType0.from_dict(data)

                return channels_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(CreatePartnerRequestChannelsType0 | None | Unset, data)

        channels = _parse_channels(d.pop("channels", UNSET))

        def _parse_llm_selection(data: object) -> CreatePartnerRequestLlmSelectionType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                llm_selection_type_0 = CreatePartnerRequestLlmSelectionType0.from_dict(data)

                return llm_selection_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(CreatePartnerRequestLlmSelectionType0 | None | Unset, data)

        llm_selection = _parse_llm_selection(d.pop("llm_selection", UNSET))

        def _parse_backup_llm_selection(data: object) -> CreatePartnerRequestBackupLlmSelectionType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                backup_llm_selection_type_0 = CreatePartnerRequestBackupLlmSelectionType0.from_dict(data)

                return backup_llm_selection_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(CreatePartnerRequestBackupLlmSelectionType0 | None | Unset, data)

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

        def _parse_assets(data: object) -> AssetSpec | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                assets_type_0 = AssetSpec.from_dict(data)

                return assets_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(AssetSpec | None | Unset, data)

        assets = _parse_assets(d.pop("assets", UNSET))

        start = d.pop("start", UNSET)

        create_partner_request = cls(
            name=name,
            workspace_id=workspace_id,
            partner_id=partner_id,
            description=description,
            soul=soul,
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
            assets=assets,
            start=start,
        )

        create_partner_request.additional_properties = d
        return create_partner_request

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
