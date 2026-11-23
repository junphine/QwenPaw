# -*- coding: utf-8 -*-
"""Agent Flow Designer — PawApp backend (assembly only).

Implementation lives in the ``afd`` package next to this file; the
execution engine lives in ``engine``. This module wires them together
and exposes ``app`` / ``plugin`` for the PluginLoader. Persistence paths
and DB initialisation live in ``afd.store``.
"""

import os
import sys

_BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

from fastapi import APIRouter  # noqa: E402

from qwenpaw.pawapp import PawApp  # noqa: E402

from engine import get_logger  # noqa: E402

import afd.nodes  # noqa: E402,F401  — registers all six node handlers
from afd import routes_executions, routes_workflows  # noqa: E402
from afd import routes_alias
logger = get_logger(__name__)

router = APIRouter()
routes_workflows.register_routes(router)
routes_executions.register_routes(router)
routes_alias.register_routes(router)

# ── PawApp instance ─────────────────────────────────────────────────
app = PawApp("Agent Flow Designer", app_id="agent-flow-designer")
app.include_router(router)

# The 'plugin' variable is what PluginLoader looks for.
plugin = app
