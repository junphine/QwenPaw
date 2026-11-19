"""
Daydayup Memory Tool Functions
Exposes memory service functions as QwenPaw agent tools
"""

import logging
import sys
import os
from pathlib import Path
from typing import Optional, List, Dict, Any

from qwenpaw.runtime.tool_registry import tool_descriptor
from agentscope.tool import ToolResponse
from agentscope.message import TextBlock
from backend.core.app import Application
logger = logging.getLogger("daydayup_memory_tool")


# 导入Daydayup服务
# 全局服务实例
_core_application: Application = None

def init_application(app: Application):
    global _core_application
    _core_application = app

def _get_memory_service():
    """获取或创建记忆服务实例"""
    global _core_application
    if _core_application is None:
        logger.error(f"[DaydayupMemoryTool] Failed to initialize core application")
    return _core_application.get_service('memory')


@tool_descriptor(name="save_memory", description="Save a memory to the Daydayup memory system",enabled_by_default=False)
async def save_memory(content: str, layer: str = "l1") -> ToolResponse:
    """Save a memory to the Daydayup memory system.

    Args:
        content: The memory content to save
        layer: Memory layer to save to (l1, l2, or l3)

    Returns:
        ToolResponse with the result
    """
    try:
        logger.info(f"[DaydayupMemoryTool] save_memory called with content length={len(content)}, layer={layer}")
        service = _get_memory_service()
        memory_id = service.save_memory(content, layer=layer)
        return ToolResponse(content=[TextBlock(type="text", text=f"Memory saved successfully with ID: {memory_id}")])
    except Exception as e:
        logger.error(f"[DaydayupMemoryTool] Error in save_memory: {e}", exc_info=True)
        return ToolResponse(content=[TextBlock(type="text", text=f"Error saving memory: {str(e)}")])


@tool_descriptor(name="search_memories", description="Search memories in the Daydayup memory system",enabled_by_default=False)
async def search_memories(query: str, layers: Optional[List[str]] = None) -> ToolResponse:
    """Search memories in the Daydayup memory system.

    Args:
        query: Search query string
        layers: List of memory layers to search (l1, l2, l3). If None, searches all layers.

    Returns:
        ToolResponse with search results
    """
    try:
        logger.info(f"[DaydayupMemoryTool] search_memories called with query='{query}', layers={layers}")
        service = _get_memory_service()
        results = service.search_memories(query, layers=layers)

        if not results:
            return ToolResponse(content=[TextBlock(type="text", text=f"No memories found matching: {query}")])

        # Format results for display
        formatted_results = []
        for i, result in enumerate(results[:10]):  # Limit to 10 results
            content_preview = result.get('content', '')[:100]
            if len(result.get('content', '')) > 100:
                content_preview += "..."
            formatted_results.append(f"{i+1}. [{result.get('layer', 'unknown')}] {content_preview}")

        result_text = f"Found {len(results)} memories:\n" + "\n".join(formatted_results)
        if len(results) > 10:
            result_text += f"\n... and {len(results) - 10} more results"

        return ToolResponse(content=[TextBlock(type="text", text=result_text)])
    except Exception as e:
        logger.error(f"[DaydayupMemoryTool] Error in search_memories: {e}", exc_info=True)
        return ToolResponse(content=[TextBlock(type="text", text=f"Error searching memories: {str(e)}")])


@tool_descriptor(name="get_memory_stats", description="Get statistics about the Daydayup memory system",enabled_by_default=False)
async def get_memory_stats() -> ToolResponse:
    """Get statistics about the Daydayup memory system.

    Returns:
        ToolResponse with memory system statistics
    """
    try:
        logger.info("[DaydayupMemoryTool] get_memory_stats called")
        service = _get_memory_service()
        stats = service.get_stats()

        result_text = f"""Daydayup Memory System Statistics:
L1 (Working Memory): {stats.get('l1_count', 0)} items
L2 (Semantic Memory): {stats.get('l2_count', 0)} items
L3 (Episodic Memory): {stats.get('l3_count', 0)} items
Total: {sum(stats.get(k, 0) for k in ['l1_count', 'l2_count', 'l3_count'])} items"""

        return ToolResponse(content=[TextBlock(type="text", text=result_text)])
    except Exception as e:
        logger.error(f"[DaydayupMemoryTool] Error in get_memory_stats: {e}", exc_info=True)
        return ToolResponse(content=[TextBlock(type="text", text=f"Error getting memory stats: {str(e)}")])