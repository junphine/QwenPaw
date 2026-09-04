# -*- coding: utf-8 -*-
"""
PawApp SDK Compatibility Bridge
================================
Provides the same API as ``qwenpaw.pawapp`` (v2.0.1+), so plugin code can
be written against the stable PawApp SDK surface today.

When QwenPaw v2.0.1+ is available (Python ≥3.11), change the import to::

    from qwenpaw.pawapp import PawApp, get_ctx, PawAppContext
    from qwenpaw.pawapp.task import SSEChannel

and delete this file.  No other code changes needed.
"""
from __future__ import annotations

import asyncio
import inspect
import json
import logging
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any, AsyncIterator, Callable, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse

# ── Detect real SDK ──────────────────────────────────────────────────
try:
    from qwenpaw.pawapp import PawApp as _RealPawApp  # noqa: F811
    from qwenpaw.pawapp import get_ctx as _real_get_ctx  # noqa: F811
    from qwenpaw.pawapp.task import SSEChannel as _RealSSE  # noqa: F811

    HAS_REAL_SDK = True
except ImportError:
    HAS_REAL_SDK = False

logger = logging.getLogger("p_plugin.pawapp_compat")

# =====================================================================
#  SSE Channel  (模拟 qwenpaw.pawapp.task.SSEChannel)
# =====================================================================
class SSEChannel:
    """Server-Sent Events channel for real-time streaming.
    
    Works like the real SDK's SSEChannel but falls back to our own
    asyncio-based implementation when the SDK is unavailable.
    """

    def __init__(self):
        self._queue: asyncio.Queue[Optional[str]] = asyncio.Queue()
        self._closed = False

    async def send_event(self, data: dict):
        """Send a JSON event through the channel."""
        if self._closed:
            return
        payload = f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
        await self._queue.put(payload)

    def close(self):
        """Close the channel (flush remaining)."""
        if not self._closed:
            self._closed = True
            self._queue.put_nowait(None)

    async def __aiter__(self) -> AsyncIterator[str]:
        """Iterate over events until closed or cancelled."""
        while True:
            try:
                chunk = await self._queue.get()
                if chunk is None:
                    return
                yield chunk
            except asyncio.CancelledError:
                return


# =====================================================================
#  App Storage  (模拟 ctx.storage)
# =====================================================================
@dataclass
class AppStorage:
    """Namespaced KV storage backed by a JSON file.

    API matches ``PawAppContext.storage`` in the real SDK.
    """
    data_dir: Path
    _namespace: str = ""
    _cache: Dict[str, Any] = field(default_factory=dict)
    _dirty: bool = False

    def _file_path(self) -> Path:
        return self.data_dir / f"storage_{self._namespace}.json"

    def _load(self):
        fp = self._file_path()
        if fp.exists():
            try:
                with open(fp, "r", encoding="utf-8") as f:
                    self._cache = json.load(f)
            except Exception:
                self._cache = {}
        else:
            self._cache = {}

    def _save(self):
        if not self._dirty:
            return
        fp = self._file_path()
        fp.parent.mkdir(parents=True, exist_ok=True)
        with open(fp, "w", encoding="utf-8") as f:
            json.dump(self._cache, f, ensure_ascii=False, indent=2)
        self._dirty = False

    async def get(self, key: str, default: Any = None) -> Any:
        """Get a key from storage."""
        self._load()
        return self._cache.get(key, default)

    async def set(self, key: str, value: Any) -> None:
        """Set a key in storage."""
        self._load()
        self._cache[key] = value
        self._dirty = True
        self._save()

    async def delete(self, key: str) -> None:
        """Delete a key from storage."""
        self._load()
        self._cache.pop(key, None)
        self._dirty = True
        self._save()

    async def keys(self) -> List[str]:
        """List all keys."""
        self._load()
        return list(self._cache.keys())


# =====================================================================
#  PawAppContext  (模拟 qwenpaw.pawapp.PawAppContext)
# =====================================================================
@dataclass
class PawAppContext:
    """Request-scoped context injected via ``Depends(get_ctx)``.

    Provides the same property surface as the real SDK:
      - ``ctx.storage`` — KV persistence
      - ``ctx.chat()`` — agent call (our 4-step)
      - ``ctx.toast()`` — frontend toast
    """
    request: Request
    app_id: str
    data_dir: Path

    @property
    def storage(self) -> AppStorage:
        """Namespaced KV storage for this app."""
        if not hasattr(self, "_storage"):
            self._storage = AppStorage(
                data_dir=self.data_dir / "pawapp_storage",
                _namespace=self.app_id,
            )
        return self._storage

    async def chat(self, prompt: str, session_id: str = "", **kwargs) -> Any:
        """Call an agent.  Returns a simple response object.

        This is a thin wrapper; the real SDK delegates to
        ``Workspace.stream_query()``.  Here we just return the text for now.
        """
        # 实际上我们在 _handle_group_chat 中自行调用智能体
        # 此处保留接口一致性
        from .p_plugin_main import call_agent_with_context
        return await call_agent_with_context(
            agent_id=kwargs.get("agent_id", ""),
            agent_name=kwargs.get("agent_name", ""),
            personality=kwargs.get("personality", ""),
            room_id=kwargs.get("room_id", ""),
            user_msg=None,
            all_messages=kwargs.get("messages", []),
        )

    async def toast(self, message: str, type: str = "info"):
        """Send a toast notification to the frontend."""
        logger.info(f"[PawApp] Toast ({type}): {message}")


# =====================================================================
#  get_ctx dependency
# =====================================================================
async def get_ctx(request: Request) -> PawAppContext:
    """FastAPI dependency that provides a request-scoped PawAppContext.

    Usage::

        @router.get("/hello")
        async def hello(ctx=Depends(get_ctx)):
            await ctx.storage.set("key", "value")
            return {"msg": "hello"}
    """
    app_id = getattr(request.state, "app_id", "p_plugin")
    data_dir = Path(getattr(request.state, "data_dir", ""))
    return PawAppContext(request=request, app_id=app_id, data_dir=data_dir)


# =====================================================================
#  PawApp  (模拟 qwenpaw.pawapp.PawApp)
# =====================================================================
class PawApp:
    """PawApp — decorator-based SDK for building app-type plugins.

    Usage::

        app = PawApp(name="My App", app_id="my_app")

        @app.route("/hello")
        async def hello(ctx=Depends(get_ctx)):
            return {"msg": "hello"}

        @app.tool("my_tool", "Description")
        async def my_tool(ctx=Depends(get_ctx), arg: str = ""):
            return {"result": arg}

        plugin = app  # PluginLoader looks for 'plugin'
    """

    def __init__(
        self,
        name: str = "",
        *,
        app_id: str = "",
        data_dir: Optional[Path] = None,
    ):
        self.name = name or app_id
        self.app_id = app_id
        self._router = APIRouter()
        self._tools: List[dict] = []
        self._commands: List[dict] = []
        self._hooks: Dict[str, Callable] = {}
        self._routers: List[APIRouter] = []
        self._data_dir = data_dir or Path(os.path.dirname(__file__)) / "data"

    # ── HTTP route decorator ────────────────────────────────────────
    def route(self, path: str, *, methods: Optional[List[str]] = None):
        """Register an HTTP route handler.

        The handler receives ``ctx`` as first positional arg (injected
        automatically via ``get_ctx``).
        """
        if methods is None:
            methods = ["POST"]

        def decorator(func: Callable) -> Callable:
            sig = inspect.signature(func)
            params = list(sig.parameters.keys())

            if params and params[0] == "ctx":
                @wraps(func)
                async def wrapped(*args, **kwargs):
                    request: Request = kwargs.get("request")
                    if request is not None:
                        ctx = await get_ctx(request)
                        return await func(ctx, *args, **kwargs)
                    return await func(*args, **kwargs)

                self._router.add_api_route(
                    path, wrapped, methods=methods, include_in_schema=False
                )
            else:
                self._router.add_api_route(
                    path, func, methods=methods, include_in_schema=False
                )
            return func

        return decorator

    # ── Agent tool decorator ────────────────────────────────────────
    def tool(self, name: str, description: str = ""):
        """Register an agent tool."""
        def decorator(func: Callable) -> Callable:
            self._tools.append({
                "name": name,
                "description": description,
                "func": func,
            })
            return func
        return decorator

    # ── Include sub-router ──────────────────────────────────────────
    def include_router(self, router: APIRouter):
        """Mount a FastAPI ``APIRouter`` under this app."""
        self._routers.append(router)

    # ── Lifecycle hooks ─────────────────────────────────────────────
    def on_launch(self, func: Callable):
        """Register a startup handler (called when app is loaded)."""
        self._hooks["launch"] = func
        return func

    def on_terminate(self, func: Callable):
        """Register a shutdown handler (called when app is unloaded)."""
        self._hooks["terminate"] = func
        return func

    # ── PluginLoader API ────────────────────────────────────────────
    def register(self, api) -> dict:
        """Called by PluginLoader to wire the app into QwenPaw.

        Returns a dict with: routes, tools, commands, hooks, lifecycle.
        This matches what the real SDK returns.

        ★ CRITICAL FIX: Also call api.register_http_router() explicitly,
        because the PluginLoader may not process the 'routes' list
        for type 'app' (PawApp) plugins. Without this, routes are
        NOT mounted and all API calls return 404/405.
        """
        routes = [self._router] + self._routers

        # ★ Explicit route registration — ensures routes are always mounted
        for idx, r in enumerate(routes):
            if r.routes:  # only register non-empty routers
                try:
                    api.register_http_router(r, prefix="/api/plugins/p_plugin", tags=["p-plugin"])
                    logger.info(f"[PawAppCompat] Registered router #{idx} with {len(r.routes)} routes at /api/plugins/p_plugin")
                except Exception as e:
                    logger.warning(f"[PawAppCompat] Route registration #{idx} failed: {e}")

        tools = []
        for t in self._tools:
            tools.append({
                "name": t["name"],
                "description": t.get("description", ""),
                "handler": t["func"],
            })

        hooks = {}
        if "launch" in self._hooks:
            hooks["on_launch"] = self._hooks["launch"]
        if "terminate" in self._hooks:
            hooks["on_terminate"] = self._hooks["terminate"]

        return {
            "routes": routes,
            "tools": tools,
            "commands": self._commands,
            "hooks": hooks,
            "lifecycle": {
                "data_dir": str(self._data_dir),
                "app_id": self.app_id,
            },
        }


# ── Conditional: use real SDK if available ───────────────────────────
if HAS_REAL_SDK:
    # Export real SDK classes for when environment supports it
    pass  # Our bridge classes take priority for backward compat
