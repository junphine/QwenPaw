"""
Daydayup Memory Tool Plugin Entry Point
Implements all 8 steps for QwenPaw 2.0 tool plugin
"""

import importlib.util
import logging
import os
from pathlib import Path

from qwenpaw.plugins.api import PluginApi
from qwenpaw.governance.tool_registry import DEFAULT_REGISTRY
from qwenpaw.modes.base import AgentMode

logger = logging.getLogger("daydayup_memory_tool")
_PLUGIN_DIR = os.path.dirname(os.path.abspath(__file__))


def _load_tool_module():
    """Load the tool functions from tools.py"""
    tool_path = os.path.join(_PLUGIN_DIR, "tools.py")
    spec = importlib.util.spec_from_file_location("daydayup_memory_tools", tool_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class DaydayupMemoryToolPlugin:
    """Daydayup Memory Tool Plugin - Exposes memory service functions as agent tools"""

    def __init__(self):
        self.name = "Daydayup Memory Tool"
        self.version = "1.0.0"
        self.id = "daydayup_memory_tool"

    def register(self, api: PluginApi):
        """Register the plugin with QwenPaw"""
        logger.info(f"[{self.id}] Registering plugin...")

        # Load tool functions
        try:
            tool = _load_tool_module()
        except Exception as e:
            logger.error(f"[{self.id}] Failed to load tool module: {e}")
            return

        # Get tool functions and their descriptors
        tool_functions = [
            ("save_memory", tool.save_memory),
            ("search_memories", tool.search_memories),
            ("get_memory_stats", tool.get_memory_stats)
        ]

        # Validate all tools have descriptors
        tool_descs = []
        for name, func in tool_functions:
            desc = getattr(func, "_tool_descriptor", None)
            if desc is None:
                logger.error(f"[{self.id}] FATAL: no _tool_descriptor on {name} — missing @tool_descriptor?")
                return
            tool_descs.append(desc)

        logger.info(f"[{self.id}] Found {len(tool_descs)} tool descriptors")

        # C3. Config layer — frontend tool management page
        for (name, func), desc in zip(tool_functions, tool_descs):
            api.register_tool(
                tool_name=name,
                tool_func=func,
                description=desc.description,
                icon="🧠",  # Brain icon for memory tools
                enabled=True,
            )
            logger.info(f"[{self.id}] Registered tool: {name}")

        # C4. Governance — allow tool calls through security layer
        # Register each tool with governance
        tool_governance_names = {
            "save_memory": "SaveMemory",
            "search_memories": "SearchMemories",
            "get_memory_stats": "GetMemoryStats"
        }

        for tool_name, func in tool_functions:
            gov_name = tool_governance_names[tool_name]
            DEFAULT_REGISTRY.register(gov_name, "internal", "")
            DEFAULT_REGISTRY.register_python_name(tool_name, gov_name)
            logger.info(f"[{self.id}] Registered {tool_name} with governance as {gov_name}")

        # C5. ToolRegistry — register into workspace for agent visibility
        class DaydayupMemoryToolMode(AgentMode):
            name = "daydayup-memory-tool-mode"

            def tools(self):
                return tool_descs  # Return all tool descriptors

        api.register_mode(DaydayupMemoryToolMode)
        logger.info(f"[{self.id}] Registered ToolRegistry mode")

        # C6. Bootstrap injection — survive zero-downtime reload
        # Inject all tool functions for bootstrap survival
        _injected_funcs = [func for _, func in tool_functions]

        def _inject_bootstrap():
            from qwenpaw.plugins.registry import PluginRegistry
            mgr = PluginRegistry().get_workspace_manager()
            if mgr is not None and hasattr(mgr, '_bootstrap_kwargs'):
                funcs = mgr._bootstrap_kwargs.setdefault("builtin_tool_funcs", [])
                for f in _injected_funcs:
                    if f not in funcs:
                        funcs.append(f)
                        logger.info(f"[{self.id}] Injected {f.__name__} into bootstrap kwargs")

        api.register_startup_hook("bootstrap_inject_daydayup_memory_tool", _inject_bootstrap, priority=55)
        logger.info(f"[{self.id}] Registered bootstrap injection hook")

        logger.info(f"[{self.id}] Daydayup Memory Tool plugin registered successfully")


# Module-level plugin instance (required for QwenPaw 2.0)
plugin = DaydayupMemoryToolPlugin()

# Export for direct import
__all__ = ["plugin"]