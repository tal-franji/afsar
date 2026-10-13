"""afsar - Simple students' API to LLMs."""

from afsar.core import ask, get_active_adapter, reset, setup
from afsar.exceptions import (
    AfsarError,
    AuthenticationError,
    ExecutionError,
    ModelNotFoundError,
    NotSetupError,
    UnsupportedFeatureError,
)

__version__ = "1.0"

__all__ = [
    "setup",
    "ask",
    "reset",
    "get_active_adapter",
    "AfsarError",
    "NotSetupError",
    "ModelNotFoundError",
    "UnsupportedFeatureError",
    "ExecutionError",
    "AuthenticationError",
    "__version__",
]
