# -*- coding: utf-8 -*-
# pylint: disable=too-many-return-statements,too-many-branches
"""Rag tool."""

import json
import logging
import mimetypes
import time
from pathlib import Path
from typing import List,Dict

import httpx2
from agentscope.message import DataBlock, TextBlock, URLSource
from agentscope.message import ToolResultState
from qwenpaw.runtime.tool_registry import tool_descriptor
from agentscope.message import TextBlock
from agentscope.tool import ToolChunk,ToolResponse
from qwenpaw.plugins import get_tool_config
from backend.core.app import Application

logger = logging.getLogger(__name__)

# 导入Daydayup服务
# 全局服务实例
_core_application: Application = None

def init_application(app: Application):
    global _core_application
    _core_application = app

@tool_descriptor(name="list_knowledge_bases", description="List deeptutor knowledge bases.", enabled_by_default=False)
async def list_knowledge_bases(
) -> ToolChunk:
    """List deeptutor knowledge bases.
    Returns:
        ToolChunk:
            Contains the list of knowledge info and metadata.
    """
    try:
        # Get tool config (API key and endpoint)
        tool_config = _core_application.config
        if not tool_config:
            return ToolChunk(
                state=ToolResultState.ERROR,
                content=[
                    TextBlock(
                        type="text",
                        text=(
                            "Error: Tool not configured. "
                            "Please set your API key in the tool settings."
                        ),
                    ),
                ],
            )

        workspace = tool_config.get_workspace()
        api_key = tool_config.get_token()
        # Get endpoint from config, use default if not set
        endpoint = tool_config.get("deeptutor_api_endpoint")
        if not endpoint or not endpoint.strip():
            endpoint = "http://127.0.0.1:8001"

        # Get timeout from config, use default if not set
        timeout = tool_config.get("timeout")
        if timeout is None or timeout <= 0:
            timeout = 60.0
        else:
            timeout = float(timeout)

        headers = {}
        if workspace:
            headers['x-deeptutor-workspace'] = workspace

        from deep_tutor_api_client import AuthenticatedClient
        from deep_tutor_api_client.api.knowledge_bases import list_kbs_knowledge_bases
        from deep_tutor_api_client.types import Response

        client = AuthenticatedClient(base_url=endpoint,token=api_key,timeout=httpx2.Timeout(timeout),headers=headers)
        with client as client:
            response:Response = await list_kbs_knowledge_bases.asyncio_detailed(client=client)

        if response.status_code != 200:
            error_msg = f"DeepTutor API error: {response.status_code}"
            try:
                error_data = response.content.decode("utf-8")
                if error_data:
                    error_msg += f" - {error_data}"
            except Exception:
                pass
            logger.error(error_msg)
            return ToolChunk(
                state=ToolResultState.ERROR,
                content=[
                    TextBlock(type="text",  text=error_msg)
                ],
            )

        # Parse response
        result = []
        for kb in response.parsed:
            if 'type' in kb.metadata and kb.metadata['type']=='subagent':
                continue
            type = kb.metadata['rag_provider']
            desc = kb.metadata['description']
            last_updated = kb.metadata['last_updated']
            result.append(dict(rag_provider=type,name=kb.name,description=desc,status=kb.status,last_updated=last_updated))

        # Return kbs
        return ToolChunk(
            state=ToolResultState.SUCCESS,
            content=[
                TextBlock(
                    type="text",
                    text=json.dumps(result,ensure_ascii=False),
                ),
            ],
        )

    except httpx2.TimeoutException:
        logger.error("list_knowledge_bases timed out")
        return ToolChunk(
            state=ToolResultState.ERROR,
            content=[
                TextBlock(
                    type="text",
                    text=(
                        "Error: list_knowledge_bases timed out. "
                        "Please try again."
                    ),
                ),
            ],
        )
    except Exception as e:
        logger.error(f"list_knowledge_bases failed: {e}", exc_info=True)
        return ToolChunk(
            state=ToolResultState.ERROR,
            content=[
                TextBlock(
                    type="text",
                    text=f"Error: list_knowledge_bases failed - {str(e)}",
                ),
            ],
        )

@tool_descriptor(name="rag_search", description="Run a RAG query against a knowledge base",enabled_by_default=False)
async def rag_search(  # pylint: disable=too-many-statements
        query: str,
        kb_name: str,
        top_k: int = 10,
        rewrite: bool = False
) -> ToolChunk:
    """Run a RAG query against a knowledge base

    Args:
        query (str):
            Text description of user question.
        kb_name (str):
            knowledge base name
        top_k (int, optional):
            top k
        rewrite (bool, optional):
            rewrite text to fix knowledge, Defaults to "false".

    Returns:
        ToolChunk:
            Contains the rag content and metadata.
    """
    try:
        # Get tool config (API key and endpoint)
        tool_config = _core_application.config
        if not tool_config:
            return ToolChunk(
                state=ToolResultState.ERROR,
                content=[
                    TextBlock(
                        type="text",
                        text=(
                            "Error: Tool not configured. "
                            "Please set your API key in the tool settings."
                        ),
                    ),
                ],
            )

        api_key = tool_config.get_token()
        # Get endpoint from config, use default if not set
        endpoint = tool_config.get("deeptutor_api_endpoint")
        if not endpoint or not endpoint.strip():
            endpoint = "http://127.0.0.1:8001"

        # Get timeout from config, use default if not set
        timeout = tool_config.get("timeout")
        if timeout is None or timeout <= 0:
            timeout = 60.0
        else:
            timeout = float(timeout)

        from deep_tutor_api_client import AuthenticatedClient
        from deep_tutor_api_client.models.knowledge_base_search_request import KnowledgeBaseSearchRequest
        from deep_tutor_api_client.api.knowledge_bases import search_kb_search
        from deep_tutor_api_client.types import Response

        client = AuthenticatedClient(base_url=endpoint,token=api_key,timeout=httpx2.Timeout(timeout))
        body = KnowledgeBaseSearchRequest(query,top_k,rewrite)

        with client as client:
            response:Response = await search_kb_search.asyncio_detailed(kb_name,client=client,body=body)

        if response.status_code != 200:
            error_msg = f"DeepTutor API error: {response.status_code}"
            try:
                error_data = response.content.decode("utf-8")
                if error_data:
                    error_msg += f" - {error_data}"
            except Exception:
                pass
            logger.error(error_msg)
            return ToolChunk(
                state=ToolResultState.ERROR,
                content=[
                    TextBlock(type="text",  text=error_msg)
                ],
            )

        # Parse response
        answer = response.parsed['answer']

        # Return kbs
        return ToolChunk(
            state=ToolResultState.SUCCESS,
            content=[
                TextBlock(
                    type="text",
                    text=answer,
                ),
            ],
        )

    except httpx2.TimeoutException:
        logger.error("rag_search timed out")
        return ToolChunk(
            state=ToolResultState.ERROR,
            content=[
                TextBlock(
                    type="text",
                    text=(
                        "Error: rag_search timed out. "
                        "Please try again."
                    ),
                ),
            ],
        )
    except Exception as e:
        logger.error(f"rag_search failed: {e}", exc_info=True)
        return ToolChunk(
            state=ToolResultState.ERROR,
            content=[
                TextBlock(
                    type="text",
                    text=f"Error: rag_search failed - {str(e)}",
                ),
            ],
        )
