from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.mcp_server_config_auth import MCPServerConfigAuth, check_mcp_server_config_auth
from ..models.mcp_server_config_type_type_0 import MCPServerConfigTypeType0, check_mcp_server_config_type_type_0
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.env import Env
    from ..models.headers import Headers


T = TypeVar("T", bound="MCPServerConfig")


@_attrs_define
class MCPServerConfig:
    """One MCP server entry.

    ``type`` is auto-detected when omitted: ``command`` ⇒ stdio; a ``url``
    ending in ``/sse`` ⇒ sse; any other ``url`` ⇒ streamableHttp.

        Attributes:
            type_ (MCPServerConfigTypeType0 | None | Unset):
            command (str | Unset):  Default: ''.
            args (list[str] | Unset):
            env (Env | Unset):
            cwd (str | Unset):  Default: ''.
            url (str | Unset):  Default: ''.
            headers (Headers | Unset):
            tool_timeout (int | Unset):  Default: 30.
            enabled_tools (list[str] | Unset):
            disabled_tools (list[str] | Unset):
            enabled (bool | Unset):  Default: True.
            allow_private_network (bool | Unset):  Default: False.
            auth (MCPServerConfigAuth | Unset):  Default: ''.
            catalog_entry (str | Unset):  Default: ''.
    """

    type_: MCPServerConfigTypeType0 | None | Unset = UNSET
    command: str | Unset = ""
    args: list[str] | Unset = UNSET
    env: Env | Unset = UNSET
    cwd: str | Unset = ""
    url: str | Unset = ""
    headers: Headers | Unset = UNSET
    tool_timeout: int | Unset = 30
    enabled_tools: list[str] | Unset = UNSET
    disabled_tools: list[str] | Unset = UNSET
    enabled: bool | Unset = True
    allow_private_network: bool | Unset = False
    auth: MCPServerConfigAuth | Unset = ""
    catalog_entry: str | Unset = ""
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_: None | str | Unset
        if isinstance(self.type_, Unset):
            type_ = UNSET
        elif isinstance(self.type_, str):
            type_ = self.type_
        else:
            type_ = self.type_

        command = self.command

        args: list[str] | Unset = UNSET
        if not isinstance(self.args, Unset):
            args = self.args

        env: dict[str, Any] | Unset = UNSET
        if not isinstance(self.env, Unset):
            env = self.env.to_dict()

        cwd = self.cwd

        url = self.url

        headers: dict[str, Any] | Unset = UNSET
        if not isinstance(self.headers, Unset):
            headers = self.headers.to_dict()

        tool_timeout = self.tool_timeout

        enabled_tools: list[str] | Unset = UNSET
        if not isinstance(self.enabled_tools, Unset):
            enabled_tools = self.enabled_tools

        disabled_tools: list[str] | Unset = UNSET
        if not isinstance(self.disabled_tools, Unset):
            disabled_tools = self.disabled_tools

        enabled = self.enabled

        allow_private_network = self.allow_private_network

        auth: str | Unset = UNSET
        if not isinstance(self.auth, Unset):
            auth = self.auth

        catalog_entry = self.catalog_entry

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if type_ is not UNSET:
            field_dict["type"] = type_
        if command is not UNSET:
            field_dict["command"] = command
        if args is not UNSET:
            field_dict["args"] = args
        if env is not UNSET:
            field_dict["env"] = env
        if cwd is not UNSET:
            field_dict["cwd"] = cwd
        if url is not UNSET:
            field_dict["url"] = url
        if headers is not UNSET:
            field_dict["headers"] = headers
        if tool_timeout is not UNSET:
            field_dict["tool_timeout"] = tool_timeout
        if enabled_tools is not UNSET:
            field_dict["enabled_tools"] = enabled_tools
        if disabled_tools is not UNSET:
            field_dict["disabled_tools"] = disabled_tools
        if enabled is not UNSET:
            field_dict["enabled"] = enabled
        if allow_private_network is not UNSET:
            field_dict["allow_private_network"] = allow_private_network
        if auth is not UNSET:
            field_dict["auth"] = auth
        if catalog_entry is not UNSET:
            field_dict["catalog_entry"] = catalog_entry

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.env import Env  # noqa: PLC0415
        from ..models.headers import Headers  # noqa: PLC0415

        d = dict(src_dict)

        def _parse_type_(data: object) -> MCPServerConfigTypeType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                type_type_0 = check_mcp_server_config_type_type_0(data)

                return type_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(MCPServerConfigTypeType0 | None | Unset, data)

        type_ = _parse_type_(d.pop("type", UNSET))

        command = d.pop("command", UNSET)

        args = cast(list[str], d.pop("args", UNSET))

        _env = d.pop("env", UNSET)
        env: Env | Unset
        if isinstance(_env, Unset):
            env = UNSET
        else:
            env = Env.from_dict(_env)

        cwd = d.pop("cwd", UNSET)

        url = d.pop("url", UNSET)

        _headers = d.pop("headers", UNSET)
        headers: Headers | Unset
        if isinstance(_headers, Unset):
            headers = UNSET
        else:
            headers = Headers.from_dict(_headers)

        tool_timeout = d.pop("tool_timeout", UNSET)

        enabled_tools = cast(list[str], d.pop("enabled_tools", UNSET))

        disabled_tools = cast(list[str], d.pop("disabled_tools", UNSET))

        enabled = d.pop("enabled", UNSET)

        allow_private_network = d.pop("allow_private_network", UNSET)

        _auth = d.pop("auth", UNSET)
        auth: MCPServerConfigAuth | Unset
        if isinstance(_auth, Unset):
            auth = UNSET
        else:
            auth = check_mcp_server_config_auth(_auth)

        catalog_entry = d.pop("catalog_entry", UNSET)

        mcp_server_config = cls(
            type_=type_,
            command=command,
            args=args,
            env=env,
            cwd=cwd,
            url=url,
            headers=headers,
            tool_timeout=tool_timeout,
            enabled_tools=enabled_tools,
            disabled_tools=disabled_tools,
            enabled=enabled,
            allow_private_network=allow_private_network,
            auth=auth,
            catalog_entry=catalog_entry,
        )

        mcp_server_config.additional_properties = d
        return mcp_server_config

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
