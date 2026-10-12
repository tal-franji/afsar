"""Tests for CLI and remote adapters."""

import subprocess
from unittest.mock import MagicMock, patch

import pytest

from afsar.adapters.agy import AgyAdapter
from afsar.adapters.claude import ClaudeAdapter
from afsar.exceptions import AuthenticationError


def test_claude_adapter_cmd_args() -> None:
    """ClaudeAdapter should construct the correct command args including permissions."""
    adapter = ClaudeAdapter(model="sonnet", tools=["python", "files"])

    mock_res = MagicMock(spec=subprocess.CompletedProcess)
    mock_res.returncode = 0
    mock_res.stdout = '{"type":"result","result":"42"}'
    mock_res.stderr = ""

    with patch("subprocess.run", return_value=mock_res) as mock_run:
        ans = adapter.ask("What is 6*7?", thinking=True)
        assert ans == "42"

        mock_run.assert_called_once()
        cmd = mock_run.call_args[0][0]
        assert "claude" in cmd
        assert "-p" in cmd
        assert "--dangerously-skip-permissions" in cmd
        assert "--model" in cmd
        assert "sonnet" in cmd
        assert "--effort" in cmd
        assert "high" in cmd


def test_agy_adapter_cmd_args() -> None:
    """AgyAdapter should construct the correct command args for agy CLI."""
    adapter = AgyAdapter(model="gemini-2.5", tools=["python", "files"])

    mock_res = MagicMock(spec=subprocess.CompletedProcess)
    mock_res.returncode = 0
    mock_res.stdout = '{"status":"SUCCESS","response":"Hello from agy"}'
    mock_res.stderr = ""

    with patch("subprocess.run", return_value=mock_res) as mock_run:
        ans = adapter.ask("Hi", thinking=False)
        assert ans == "Hello from agy"

        mock_run.assert_called_once()
        cmd = mock_run.call_args[0][0]
        assert "agy" in cmd
        assert "-p" in cmd
        assert "--dangerously-skip-permissions" in cmd
        assert "--model" in cmd
        assert "gemini-2.5" in cmd
        assert "--effort" in cmd
        assert "low" in cmd


def test_claude_adapter_authentication_error() -> None:
    """ClaudeAdapter should raise AuthenticationError when OAuth token is invalid."""
    adapter = ClaudeAdapter()

    mock_res = MagicMock(spec=subprocess.CompletedProcess)
    mock_res.returncode = 0
    mock_res.stdout = (
        '{"is_error": true, "result": "Failed to authenticate. API Error: 401 '
        '{\\"type\\":\\"error\\",\\"error\\":{\\"type\\":\\"authentication_error\\",'
        '\\"message\\":\\"OAuth access token is invalid.\\"}}"}'
    )
    mock_res.stderr = ""

    with patch("subprocess.run", return_value=mock_res):
        with pytest.raises(AuthenticationError, match="claude auth login"):
            adapter.ask("Hello")
