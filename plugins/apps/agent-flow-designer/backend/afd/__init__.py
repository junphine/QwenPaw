# -*- coding: utf-8 -*-
"""AFD implementation package.

Puts the backend dir on sys.path so ``engine`` is importable without
going through main.py — the engine + handlers must work headless.
"""

import os
import sys

_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)
