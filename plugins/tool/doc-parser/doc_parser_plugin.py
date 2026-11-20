# -*- coding: utf-8 -*-
"""Qwen-Image Tool Plugin Entry Point."""

import importlib.util
import logging
import os
from pathlib import Path
from qwenpaw.plugins.api import PluginApi
from agentscope.message import DataBlock, TextBlock, URLSource
from agentscope.message import ToolResultState
from agentscope.tool import ToolChunk
from qwenpaw.constant import DEFAULT_MEDIA_DIR
from qwenpaw.plugins import get_tool_config
from qwenpaw.app.agent_context import get_current_user_id

logger = logging.getLogger(__name__)

_PLUGIN_DIR = os.path.dirname(os.path.abspath(__file__))


def mineru_parse(soure_path:str)-> ToolChunk:
    """Generate md file from document(pdf,docx,pptx,excel,etc) using MinerU model

    Args:
        soure_path: The input document path to convert
    Returns:
        ToolChunk with the md file path in result
    """
    from .mineru import config
    from .mineru import mineru_client
    mineru_config = config.resolve_mineru_config()
    uid = get_current_user_id() or 'default'
    output_base = DEFAULT_MEDIA_DIR / uid
    output_md_path = mineru_client.parse_remote(Path(soure_path),output_base,mineru_config)
    # Return path with local file path
    return ToolChunk(
        state=ToolResultState.SUCCESS,
        content=[
            DataBlock(
                source=URLSource(
                    url="file://" + str(output_md_path),
                    media_type="text/markdown",
                ),
            ),
            TextBlock(
                type="text",
                text=(
                    f"Generated md file using mineru\n"                    
                    f"From: {soure_path}\n"
                    f"Saved to: {output_md_path}\n"
                ),
            ),
        ],
    )

def docling_parse(soure_path:str)-> ToolChunk:
    """Generate md file from document(pdf,docx,pptx,excel,etc) using Docling model

    Args:
        soure_path: The input document path to convert
    Returns:
        ToolChunk with the md file path in result
    """
    from .docling import config
    from .docling import remote
    docling_config = config.resolve_docling_config()
    uid = get_current_user_id() or 'default'
    output_base = DEFAULT_MEDIA_DIR / uid
    output_md_path = remote.parse_remote(Path(soure_path),output_base,docling_config)
    # Return path with local file path
    return ToolChunk(
        state=ToolResultState.SUCCESS,
        content=[
            DataBlock(
                source=URLSource(
                    url="file://" + str(output_md_path),
                    media_type="text/markdown",
                ),
            ),
            TextBlock(
                type="text",
                text=(
                    f"Generated md file using mineru\n"
                    f"From: {soure_path}\n"
                    f"Saved to: {output_md_path}\n"
                ),
            ),
        ],
    )


class DocParserToolPlugin:
    """Documnet Parse Tool Plugin.

    Registers mineru and docling parse tools into the Agent's toolkit.
    """

    def register(self, api: PluginApi):
        """Register Doc-Parse tools.

        Args:
            api: PluginApi instance.
        """
        api.register_tool(
            tool_name="mineru_parse",
            tool_func=mineru_parse,
            description=(
                "Generate md file from document(pdf,docx,pptx,excel,etc) using MinerU model"
            ),
            icon="✏️",
            tool_type="network",
        )

        api.register_tool(
            tool_name="docling_parse",
            tool_func=docling_parse,
            description="Generate md file from document(pdf,docx,pptx,excel,etc) using Docling model",
            icon="✏️",
            tool_type="network",
        )

        logger.info("Qwen-Image tool plugin registered")


# Export plugin instance
plugin = DocParserToolPlugin()
