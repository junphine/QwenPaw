"""Dependency injection container for MCP QwenPaw Server.

This module provides a central container for managing all application dependencies,
replacing the global variables and singletons previously used throughout the codebase.
"""

from typing import Any, Dict

# Import logging from bootstrap package
from .logging_bootstrap import get_logger, update_log_levels
from .cache.parser_cache import TreeCache
from .config import *

logger = get_logger(__name__)


class DependencyContainer:
    """Container for all application dependencies."""

    def __init__(self) -> None:
        """Initialize container with all core dependencies."""
        logger.debug("Initializing dependency container")

        # Create core dependencies
        self.config_manager = ConfigurationManager()
        self._config = self.config_manager.get_config()

        self.tree_cache = TreeCache(
            max_size_mb=self._config.cache.max_size_mb, ttl_seconds=self._config.cache.ttl_seconds
        )

        # Storage for any additional dependencies
        self._additional: Dict[str, Any] = {}

    def get_config(self) -> ServerConfig:
        """Get the current configuration."""
        # Always get the latest from the config manager
        config = self.config_manager.get_config()
        return config

    def register_dependency(self, name: str, instance: Any) -> None:
        """Register an additional dependency."""
        self._additional[name] = instance

    def get_dependency(self, name: str) -> Any:
        """Get a registered dependency."""
        return self._additional.get(name)


# Create the single container instance - this will be the ONLY global
container = DependencyContainer()


def get_container() -> DependencyContainer:
    """Get the dependency container."""
    return container
