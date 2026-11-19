"""
Daydayup Memory Tool Plugin Entry Point
Implements all 8 steps for QwenPaw 2.0 tool plugin
"""
import logging
import os
import importlib
from pathlib import Path

from qwenpaw.plugins.api import PluginApi
from qwenpaw.governance.tool_registry import DEFAULT_REGISTRY,register_tool_governance
from qwenpaw.modes.base import AgentMode

_PLUGIN_DIR = os.path.dirname(os.path.abspath(__file__))


def _load_tool_module(name,app=None):
    """Load gpt_image2_tool.py from this plugin's directory via importlib."""
    tool_path = os.path.join(_PLUGIN_DIR, name+".py")
    spec = importlib.util.spec_from_file_location(
        name,
        tool_path,
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if app and hasattr(module,'init_application'):
        module.init_application(app)
    return module


logger = logging.getLogger("daydayup_memory_tool")

class DaydayupMemoryToolPlugin:
    """Daydayup Memory Tool Plugin - Exposes memory service functions as agent tools"""

    def __init__(self):
        self.name = "Daydayup Memory Tool"
        self.version = "1.7.0"
        self.id = "daydayup_memory_tool"
        self.parent = None

    def register(self, api: PluginApi):
        """Register the plugin with QwenPaw"""
        logger.info(f"[{self.id}] Registering plugin...")

        # Load tool functions
        rag_tool = _load_tool_module('rag_tool',self.parent.app)
        memory_tool = _load_tool_module('memory_tool',self.parent.app)

        # Get tool functions and their descriptors
        tool_functions = [
            ("save_memory", memory_tool.save_memory),
            ("search_memories", memory_tool.search_memories),
            ("get_memory_stats", memory_tool.get_memory_stats),
            ("list_knowledge_bases", rag_tool.list_knowledge_bases),
            ("rag_search", rag_tool.rag_search)
        ]

        # Validate all tools have descriptors
        tool_descs = []
        for name, func in tool_functions:
            desc = getattr(func, "_tool_descriptor", None)
            if desc is None:
                logger.error(f"[{self.id}] FATAL: no _tool_descriptor on {name} — missing @tool_descriptor?")
                continue
            tool_descs.append(desc)

        logger.info(f"[{self.id}] Found {len(tool_descs)} tool descriptors")

        # C3. Config layer — frontend tool management page
        for (name, func), desc in zip(tool_functions, tool_descs):
            api.register_tool(
                tool_name=name,
                tool_func=func,
                description=desc.description,
                icon="🧠",  # Brain icon for memory tools
                enabled=desc.enabled_by_default
            )
            logger.info(f"[{self.id}] Registered tool: {name}")

        if False:
            # C5. ToolRegistry — register into workspace for agent visibility
            class DaydayupMemoryToolMode(AgentMode):
                name = "daydayup-memory-tool-mode"

                def tools(self):
                    return tool_descs  # Return all tool descriptors

            api.register_mode(DaydayupMemoryToolMode)
            logger.info(f"[{self.id}] Registered ToolRegistry mode")

        logger.info(f"[{self.id}] Daydayup Memory Tool plugin registered successfully")

