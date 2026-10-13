"""Core session management and procedural API for afsar."""

import os
import shutil
from collections.abc import Sequence
from typing import Any, TypeVar, overload

from afsar.adapters.base import BaseAdapter
from afsar.exceptions import (
    ModelNotFoundError,
    NotSetupError,
    UnsupportedFeatureError,
)

T = TypeVar("T")

_active_adapter: BaseAdapter | None = None


def get_active_adapter() -> BaseAdapter | None:
    """Return the currently configured adapter, or None if not setup."""
    return _active_adapter


def reset() -> None:
    """Reset the global afsar session state. Useful for tests."""
    global _active_adapter
    _active_adapter = None


def _normalize_explicit_provider(provider: str) -> str:
    """Normalize and validate an explicitly provided provider string."""
    normalized = provider.strip().lower()
    alias_map = {
        "claude": "claude",
        "claude-code": "claude",
        "agy": "agy",
        "antigravity": "agy",
        "gemini": "gemini",
        "openai": "openai",
    }
    if normalized not in alias_map:
        raise ValueError(
            f"Unknown provider '{provider}'. Supported: 'claude', 'agy', 'gemini', 'openai'."
        )
    return alias_map[normalized]


def _find_candidate_providers(api_key: str | None = None) -> list[str]:
    """Auto-detect available providers according to priority."""
    candidates: list[str] = []
    if shutil.which("claude") is not None:
        candidates.append("claude")
    if shutil.which("agy") is not None:
        candidates.append("agy")
    if api_key or os.getenv("GEMINI_API_KEY"):
        candidates.append("gemini")
    if api_key or os.getenv("OPENAI_API_KEY"):
        candidates.append("openai")
    return candidates


def detect_providers(
    *,
    provider: str | None = None,
    api_key: str | None = None,
) -> list[str]:
    """Detect candidate providers based on explicit overrides, env vars, or auto-detection."""
    chosen = provider or os.getenv("AFSAR_PROVIDER")
    if chosen is not None:
        return [_normalize_explicit_provider(chosen)]

    candidates = _find_candidate_providers(api_key=api_key)
    if not candidates:
        raise ModelNotFoundError(
            "No local agent (claude-code, agy) or remote API keys (GEMINI_API_KEY, OPENAI_API_KEY) found."
        )
    return candidates


def detect_provider(
    *,
    provider: str | None = None,
    api_key: str | None = None,
) -> str:
    """Detect the first provider based on explicit overrides or auto-detection."""
    return detect_providers(provider=provider, api_key=api_key)[0]


def _create_adapter(
    provider: str,
    model: str | None,
    api_key: str | None,
    tools: Sequence[str] | None,
) -> BaseAdapter:
    """Instantiate the corresponding adapter instance for a provider."""
    tool_list = list(tools) if tools else []
    if provider == "claude":
        from afsar.adapters.claude import ClaudeAdapter

        return ClaudeAdapter(model=model, tools=tool_list)
    if provider == "agy":
        from afsar.adapters.agy import AgyAdapter

        return AgyAdapter(model=model, tools=tool_list)
    if provider == "gemini":
        from afsar.adapters.gemini import GeminiAdapter

        return GeminiAdapter(model=model, api_key=api_key)
    if provider == "openai":
        from afsar.adapters.openai import OpenAIAdapter

        return OpenAIAdapter(model=model, api_key=api_key)

    raise ModelNotFoundError(f"Unsupported provider '{provider}'.")


def setup(
    model: str | None = None,
    api_key: str | None = None,
    tools: Sequence[str] | None = ("python", "files"),
    provider: str | None = None,
) -> None:
    """Configure the active LLM provider and tool settings."""
    global _active_adapter

    detected = detect_provider(provider=provider, api_key=api_key)

    if bool(tools) and detected not in {"claude", "agy"}:
        raise UnsupportedFeatureError(
            f"Remote models ({detected}) do not support local code execution or file tools yet.\n"
            f"To use remote models, explicitly initialize with: afsar.setup(tools=[])"
        )

    _active_adapter = _create_adapter(detected, model, api_key, tools)


@overload
def ask(
    prompt: str,
    *,
    format: str = "text",
    schema: None = None,
    temperature: float | None = None,
    thinking: bool | None = None,
) -> str: ...


@overload
def ask(
    prompt: str,
    *,
    format: str = "text",
    schema: type[T],
    temperature: float | None = None,
    thinking: bool | None = None,
) -> T: ...


@overload
def ask(
    prompt: str,
    *,
    format: str = "text",
    schema: Any = None,
    temperature: float | None = None,
    thinking: bool | None = None,
) -> Any: ...


def ask(
    prompt: str,
    *,
    format: str = "text",
    schema: Any = None,
    temperature: float | None = None,
    thinking: bool | None = None,
) -> Any:
    """Send a prompt to the configured LLM and return the answer."""
    if _active_adapter is None:
        raise NotSetupError(
            "afsar is not configured. Please call afsar.setup() before afsar.ask()."
        )

    if format not in {"text", "json"}:
        raise ValueError(f"Invalid format '{format}'. Supported formats: 'text', 'json'.")

    if thinking is True and not _active_adapter.supports_thinking:
        raise ValueError(
            f"Thinking mode requested, but adapter '{_active_adapter.name}' does not support thinking."
        )

    return _active_adapter.ask(
        prompt,
        format=format,
        schema=schema,
        temperature=temperature,
        thinking=thinking,
    )
