"""Tests for afsar session lifecycle, auto-detection, and error handling."""

from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest

import afsar
from afsar.adapters.base import BaseAdapter
from afsar.exceptions import NotSetupError, UnsupportedFeatureError


@pytest.fixture(autouse=True)
def clean_afsar_state() -> Generator[None, None, None]:
    """Ensure afsar global state is cleared before and after each test."""
    afsar.reset()
    yield
    afsar.reset()


def test_ask_before_setup_raises_not_setup_error() -> None:
    """Calling ask() before setup() must raise NotSetupError."""
    with pytest.raises(NotSetupError, match="afsar.setup\\(\\) before afsar.ask\\(\\)"):
        afsar.ask("What is 2+2?")


def test_invalid_format_raises_value_error() -> None:
    """Invalid format values should raise ValueError."""
    mock_adapter = MagicMock(spec=BaseAdapter)
    mock_adapter.name = "mock"
    mock_adapter.supports_thinking = False

    with patch("afsar.core._active_adapter", mock_adapter):
        with pytest.raises(ValueError, match="Invalid format 'xml'"):
            afsar.ask("Hello", format="xml")


def test_thinking_on_unsupported_model_raises_value_error() -> None:
    """Requesting thinking=True on a model that does not support it raises ValueError."""
    mock_adapter = MagicMock(spec=BaseAdapter)
    mock_adapter.name = "mock"
    mock_adapter.supports_thinking = False

    with patch("afsar.core._active_adapter", mock_adapter):
        with pytest.raises(ValueError, match="does not support thinking"):
            afsar.ask("Hello", thinking=True)


def test_remote_with_default_tools_raises_unsupported_feature_error() -> None:
    """Configuring a remote provider with default tools must raise UnsupportedFeatureError."""
    with pytest.raises(UnsupportedFeatureError, match="do not support local code execution"):
        afsar.setup(provider="gemini", api_key="dummy_key", tools=["python", "files"])


def test_remote_with_empty_tools_succeeds() -> None:
    """Configuring a remote provider with tools=[] must succeed."""
    afsar.setup(provider="openai", api_key="dummy_key", tools=[])
    adapter = afsar.get_active_adapter()
    assert adapter is not None
    assert adapter.name == "openai"


def test_unknown_provider_raises_value_error() -> None:
    """Unknown provider name raises ValueError."""
    with pytest.raises(ValueError, match="Unknown provider 'nonexistent'"):
        afsar.setup(provider="nonexistent")


def test_afsar_provider_env_var_override(monkeypatch: pytest.MonkeyPatch) -> None:
    """AFSAR_PROVIDER environment variable should override default detection."""
    monkeypatch.setenv("AFSAR_PROVIDER", "gemini")
    afsar.setup(api_key="dummy_key", tools=[])
    adapter = afsar.get_active_adapter()
    assert adapter is not None
    assert adapter.name == "gemini"


def test_authentication_error_suggests_login_and_fails() -> None:
    """AuthenticationError should fail directly without fallback and advise re-authentication."""
    mock_failed = MagicMock(spec=BaseAdapter)
    mock_failed.name = "claude"
    mock_failed.supports_thinking = True
    mock_failed.ask.side_effect = afsar.AuthenticationError(
        "Claude authentication failed (OAuth access token is invalid or expired).\n"
        "Please run 'claude auth login' in your terminal to re-authenticate, "
        "or switch provider using: afsar.setup(provider='agy')"
    )

    with (
        patch("afsar.core.detect_provider", return_value="claude"),
        patch("afsar.core._create_adapter", return_value=mock_failed),
    ):
        afsar.setup()
        with pytest.raises(afsar.AuthenticationError, match="claude auth login"):
            afsar.ask("Hello")
