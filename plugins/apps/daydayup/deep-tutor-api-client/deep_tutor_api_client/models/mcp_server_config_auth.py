from typing import Literal

MCPServerConfigAuth = Literal["", "oauth"]

MCP_SERVER_CONFIG_AUTH_VALUES: set[MCPServerConfigAuth] = {
    "",
    "oauth",
}


def check_mcp_server_config_auth(value: str) -> MCPServerConfigAuth:
    if value in MCP_SERVER_CONFIG_AUTH_VALUES:
        return value
    raise TypeError(f"Unexpected value {value!r}. Expected one of {MCP_SERVER_CONFIG_AUTH_VALUES!r}")
