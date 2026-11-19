# -*- coding: utf-8 -*-
"""Node handler registry.

Maps a node ``type`` to an async-generator handler. Handlers are decoupled
from traversal: they perform the node's side effects (mutating
``ExecutionState``) and yield :class:`RunEvent` objects describing what
happened. This replaces the old inline ``if node_type == ...`` chain and makes
new node types (LLM / Code / HTTP / sub-workflow / ask) pluggable via the same
``@register_node`` decorator.

Node handlers are registered by ``backend/main.py`` (which owns the platform
helpers such as the agent chat call and router evaluation). The engine itself
stays free of platform imports to avoid circular dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Callable, Dict, List, Optional, Tuple

from .events import RunEvent
from .state import ExecutionState

# Handler signature: an async generator that yields RunEvents.
NodeHandler = Callable[["NodeRunContext"], AsyncIterator[RunEvent]]


# ── Node type metadata definitions ───────────────────────────────────────────

@dataclass(frozen=True)
class PropertyField:
    """Declarative definition of one field in the property panel."""

    name: str
    type: str  # 'text' | 'textarea' | 'select' | 'number' | 'boolean' | ...
    label: str
    required: bool = False
    default: Any = None
    description: str = ""
    placeholder: str = ""
    options: List[Dict[str, str]] = field(default_factory=list)
    condition_field: str = ""
    condition_value: Any = None


@dataclass(frozen=True)
class NodeTypeDef:
    """Complete metadata definition for a node type."""

    type_id: str
    label: str
    description: str = ""
    icon: str = "default"
    color: str = "#6366F1"
    bg_color: str = "#eef2ff"
    border_color: str = "#6366F1"
    properties: List[PropertyField] = field(default_factory=list)
    output_fields: List[Dict[str, str]] = field(default_factory=list)
    supports_error_policy: bool = False
    supports_retry: bool = False
    custom_renderer: Optional[str] = None


@dataclass
class NodeRunContext:
    """Everything a node handler needs to execute one node."""

    node: Dict[str, Any]
    state: ExecutionState
    workflow: Dict[str, Any] = field(default_factory=dict)
    live_predecessors: List[str] = field(default_factory=list)
    """Ids of the predecessors whose edge was actually taken on this run.

    Handlers use this instead of iterating every accumulated output, so a node
    never sees content from a branch the router did not select.
    """
    services: Dict[str, Any] = field(default_factory=dict)
    """Live host objects a tool node needs (workspace, agent_config, identity).

    Deliberately *not* a field of :class:`ExecutionState`: that dataclass is
    JSON-serialised for HITL checkpointing, so a live handle cannot ride in it.
    The Runner injects services when it builds each node context instead, and a
    resumed run re-resolves them from the current host process.
    """

    @property
    def node_id(self) -> str:
        return self.node.get("id", "")

    @property
    def node_type(self) -> str:
        return self.node.get("type", "")

    @property
    def config(self) -> Dict[str, Any]:
        return self.node.get("config") or {}


_REGISTRY: Dict[str, Tuple[NodeHandler, Optional[NodeTypeDef]]] = {}


def register_node(
    type_id: str, *, metadata: Optional[NodeTypeDef] = None
) -> Callable[[NodeHandler], NodeHandler]:
    """Decorator that registers ``handler`` for node type ``type_id``.

    Optional *metadata* describes the node type so the frontend can render it
    dynamically (icon, colour, property panel schema, etc.).
    """

    def decorator(handler: NodeHandler) -> NodeHandler:
        _REGISTRY[type_id] = (handler, metadata)
        return handler

    return decorator


def get_handler(type_id: str) -> Optional[NodeHandler]:
    """Return the registered handler for ``type_id`` or ``None``."""
    entry = _REGISTRY.get(type_id)
    return entry[0] if entry else None


def get_node_type_def(type_id: str) -> Optional[NodeTypeDef]:
    """Return the metadata definition for ``type_id`` or ``None``."""
    entry = _REGISTRY.get(type_id)
    return entry[1] if entry else None


def list_node_type_defs() -> List[NodeTypeDef]:
    """Return all registered node type metadata definitions."""
    return [meta for _h, meta in _REGISTRY.values() if meta is not None]


def registered_types() -> set:
    """Return the set of currently registered node type ids."""
    return set(_REGISTRY.keys())
