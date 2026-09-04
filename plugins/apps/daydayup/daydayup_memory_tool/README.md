# Daydayup Memory Tool Plugin

A QwenPaw 2.0 tool plugin that exposes the Daydayup memory service functions as agent-callable tools.

## Tools Provided

1. **save_memory** - Save a memory to the Daydayup memory system
2. **search_memories** - Search memories in the Daydayup memory system  
3. **get_memory_stats** - Get statistics about the Daydayup memory system

## Installation

1. Copy the `daydayup_memory_tool` directory to your QwenPaw plugins directory:
   ```
   cp -r daydayup_memory_tool ~/.qwenpaw/plugins/
   ```

2. Restart QwenPaw or use the plugin reload functionality:
   ```bash
   curl -s -X POST "http://127.0.0.1:22224/api/plugins/install" \
     -H "Content-Type: application/json" \
     -d '{"source": "/root/.qwenpaw/plugins/daydayup_memory_tool", "force": true}'
   ```

## Usage

Once installed, agents can call these tools:

```python
# Save a memory
await save_memory(content="Today I learned about QwenPaw plugin development", layer="l2")

# Search memories
results = await search_memories(query="QwenPaw plugin", layers=["l2", "l3"])

# Get memory statistics
stats = await get_memory_stats()
```

## Architecture

This plugin follows the QwenPaw 2.0 tool plugin 8-step process:

1. ✅ Manifest with proper qwenpaw_version
2. ✅ Tool functions with @tool_descriptor decorators
3. ✅ register_tool() with enabled=True
4. ✅ DEFAULT_REGISTRY registration for governance
5. ✅ register_mode(AgentMode) for workspace ToolRegistry
6. ✅ Bootstrap injection hook for zero-downtime reload survival
7. ✅ agentscope 2.0 API compatibility checked
8. ✅ Backend entry exports plugin instance