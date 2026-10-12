"""Base adapter interface for LLM models and local agents."""

import abc
from typing import Any


class BaseAdapter(abc.ABC):
    """Abstract base class for all model adapters."""

    name: str = "base"
    supports_tools: bool = False
    supports_thinking: bool = False
    supports_schema: bool = False

    @abc.abstractmethod
    def ask(
        self,
        prompt: str,
        *,
        format: str = "text",
        schema: Any = None,
        temperature: float | None = None,
        thinking: bool | None = None,
    ) -> Any:
        """Execute a prompt against the model and return the result."""
