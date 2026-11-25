# -*- coding: utf-8 -*-
"""Qwen-Image Tool Plugin Entry Point."""

import logging
import os
from pathlib import Path
from typing import List, Dict, Any
import anyio

from pydantic import FileUrl

from qwenpaw.plugins.api import PluginApi
from agentscope.message import DataBlock, TextBlock, URLSource
from agentscope.message import ToolResultState
from agentscope.tool import ToolChunk
from qwenpaw.constant import DEFAULT_MEDIA_DIR
from qwenpaw.plugins import get_tool_config
from qwenpaw.app.agent_context import get_current_user_id
from qwenpaw.runtime.tool_registry import tool_descriptor

logger = logging.getLogger(__name__)

_PLUGIN_DIR = os.path.dirname(os.path.abspath(__file__))


def mineru_parse_sync(sources_path:List[str])-> ToolChunk:
    """Generate md files from documents(pdf,docx,pptx,excel,etc) using MinerU model

    Args:
        sources_path: The input documents path to convert
    Returns:
        ToolChunk with the md files path in result
    """
    from .mineru import config
    from .mineru import mineru_client
    mineru_config = config.resolve_mineru_config()
    uid = get_current_user_id() or 'default'
    output_base = DEFAULT_MEDIA_DIR / uid
    output_md_path = mineru_client.parse_remote(sources_path,output_base,mineru_config)
    content=[
        TextBlock(
            type="text",
            text=(
                f"Generated md file using mineru\n"
                f"From: {sources_path}\n"
                f"Saved to: {output_md_path}\n"
            ),
        ),
    ]
    for output in output_md_path:
        data = DataBlock(
            source=URLSource(
                url=FileUrl("file://" + str(output)),
                media_type="text/markdown",
            ),
        )
        content.append(data)

    # Return path with local file path
    return ToolChunk(
        state=ToolResultState.SUCCESS,
        content=content
    )

async def mineru_parse(sources_path:List[str])-> ToolChunk:
    """Generate md files from documents(pdf,docx,pptx,excel,etc) using MinerU model

    Args:
        sources_path: The input documents path to convert
    Returns:
        ToolChunk with the md files path in result
    """
    return await anyio.to_thread.run_sync(mineru_parse_sync,sources_path)


async def docling_parse_one(source_path:str,docling_config)-> ToolChunk:
    """Generate md files from documents(pdf,docx,pptx,excel,etc) using Docling model

    Args:
        sources_path: The input documents path to convert
    Returns:
        ToolChunk with the md files path in result
    """
    from .docling import remote
    uid = get_current_user_id() or 'default'
    output_base = DEFAULT_MEDIA_DIR / uid
    md_path = await anyio.to_thread.run_sync(remote.parse_remote,Path(source_path),output_base,docling_config)
    return md_path

async def gather(*coros):
    """按输入顺序返回所有协程结果；任一失败则取消全部并抛出。"""
    results = [None] * len(coros)

    async def _runner(i, coro):
        results[i] = await coro

    async with anyio.create_task_group() as tg:
        for i, c in enumerate(coros):
            tg.start_soon(_runner, i, c)

    return results

async def docling_parse(sources_path:List[str])-> ToolChunk:
    """Generate md files from documents(pdf,docx,pptx,excel,etc) using Docling model

    Args:
        sources_path: The input documents path to convert
    Returns:
        ToolChunk with the md files path in result
    """
    from .docling import config
    docling_config = config.resolve_docling_config()
    n = len(sources_path)
    limiter = anyio.CapacityLimiter(min(8, max(n, 1)))
    output_md_path = await gather(*(
        docling_parse_one(sp, docling_config) for sp in sources_path
    ))
    content=[
        TextBlock(
            type="text",
            text=(
                f"Generated md file using docling\n"
                f"From: {sources_path}\n"
                f"Saved to: {output_md_path}\n"
            ),
        ),
    ]
    for output in output_md_path:
        data = DataBlock(
            source=URLSource(
                url=FileUrl("file://" + str(output)),
                media_type="text/markdown",
            ),
        )
        content.append(data)

    # Return path with local file path
    return ToolChunk(
        state=ToolResultState.SUCCESS,
        content=content
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
            description=mineru_parse.__doc__,
            icon="✏️",
            tool_type="network",
        )

        api.register_tool(
            tool_name="docling_parse",
            tool_func=docling_parse,
            description=docling_parse.__doc__,
            icon="✏️",
            tool_type="network",
        )

        logger.info("Qwen-Image tool plugin registered")


# Export plugin instance
plugin = DocParserToolPlugin()
