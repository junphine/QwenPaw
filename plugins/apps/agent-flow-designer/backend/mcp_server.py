"""MCP server implementation for QwenPaw with dependency injection."""

import os
from typing import Any, Dict, Optional, Tuple

from mcp.server.fastmcp import FastMCP

from .logging_bootstrap import get_logger, update_log_levels
from .di import get_container
from .afd.store import _read_all

# Create server instance
mcp = FastMCP("qwenpaw")

# Set up logger
logger = get_logger(__name__)


def main() -> None:
    """Run the server with command-line argument handling"""
    import argparse
    import sys

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="MCP QwenPaw Server - File analysis with qwen-paw")
    parser.add_argument("--host", default="127.0.0.1", help="Bind address (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8089, help="Bind port (default: 8089)")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--version", action="store_true", help="Show version and exit")

    # Parse arguments - this handles --help automatically
    args = parser.parse_args()

    host=args.host
    port=args.port

    # Set up debug logging if requested
    if args.debug:
        # Set environment variable first for consistency
        os.environ["MCP_TS_LOG_LEVEL"] = "DEBUG"
        # Then update log levels
        update_log_levels("DEBUG")
        logger.debug("Debug logging enabled")

    # Get the container
    container = get_container()

    # Register capabilities and tools
    from .tools.registration import register_tools,register_prompts,register_workflow_tool

    workflows = _read_all()
    for wf in workflows:
        deployed_version_id = wf.get("deployed_version_id")
        if deployed_version_id:
            register_workflow_tool(mcp, wf, container)

    register_tools(mcp, container)
    register_prompts(mcp,container)

    # Load configuration from environment
    config = container.get_config()

    # Update tree cache settings from config
    container.tree_cache.set_max_size_mb(config.cache.max_size_mb)
    container.tree_cache.set_enabled(config.cache.enabled)

    # Run the server
    logger.info("Starting MCP QwenPaw Server")
    mcp.settings.host = host
    mcp.settings.port = port
    logger.info("Serving qwen-paw MCP server over SSE at http://%s:%d/mcp", host, port)
    mcp.run(transport='streamable-http')


if __name__ == "__main__":
    main()
