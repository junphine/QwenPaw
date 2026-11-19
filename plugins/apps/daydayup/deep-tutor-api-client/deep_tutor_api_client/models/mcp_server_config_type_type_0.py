from typing import Literal

MCPServerConfigTypeType0 = Literal["sse", "stdio", "streamableHttp"]

MCP_SERVER_CONFIG_TYPE_TYPE_0_VALUES: set[MCPServerConfigTypeType0] = {
    "sse",
    "stdio",
    "streamableHttp",
}


def check_mcp_server_config_type_type_0(value: str) -> MCPServerConfigTypeType0:
    if value in MCP_SERVER_CONFIG_TYPE_TYPE_0_VALUES:
        return value
    raise TypeError(f"Unexpected value {value!r}. Expected one of {MCP_SERVER_CONFIG_TYPE_TYPE_0_VALUES!r}")
