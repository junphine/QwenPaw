# -*- coding: utf-8 -*-
"""Puter channel constants."""

QWENPAW_HTTP_URL = "http://127.0.0.1:8088"

DEFAULT_HTTP_URL = "http://im.puter.srv.cn:38080"

PUTER_ORIGIN_URL = "http://puter.localhost:4100"

PUTER_API_URL = "http://api.puter.localhost:4100"

# Heartbeat interval (seconds)
HEARTBEAT_INTERVAL = 30

MAX_RECONNECT_ATTEMPTS = 50

# Connection timeout (seconds)
CONNECTION_TIMEOUT = 30

# Task timeout (milliseconds)
DEFAULT_TASK_TIMEOUT_MS = 3600000  # 1 hour

# Maximum text chunk size (characters)
# Larger messages will be split to avoid WebSocket disconnection
TEXT_CHUNK_LIMIT = 4000
