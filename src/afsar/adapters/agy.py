"""Antigravity (agy) CLI subprocess adapter."""

import json
import subprocess
from typing import Any

from afsar.adapters.base import BaseAdapter
from afsar.exceptions import ExecutionError
from afsar.schema import _strip_markdown_fence, to_json_schema, validate_schema_output


class AgyAdapter(BaseAdapter):
    """Adapter for local Antigravity (agy) CLI."""

    name = "agy"
    supports_tools = True
    supports_thinking = True
    supports_schema = True

    def __init__(self, model: str | None = None, tools: list[str] | None = None) -> None:
        self.model = model
        self.tools = tools if tools is not None else ["python", "files"]

    def _build_cmd(
        self,
        prompt: str,
        format: str,
        schema: Any,
        thinking: bool | None,
    ) -> list[str]:
        cmd = ["agy", "-p", prompt, "--output-format", "json", "--dangerously-skip-permissions"]
        if self.model:
            cmd.extend(["--model", self.model])

        if schema is not None:
            cmd.extend(["--json-schema", json.dumps(to_json_schema(schema))])
        elif format == "json":
            cmd.extend(["--json-schema", json.dumps({"type": "object"})])

        if thinking is not None:
            cmd.extend(["--effort", "high" if thinking else "low"])

        return cmd

    def _parse_output(self, stdout: str) -> str:
        try:
            data = json.loads(stdout)
            if data.get("status") not in (None, "SUCCESS"):
                raise ExecutionError(f"agy error: {stdout}")
            if "structured_output" in data and data["structured_output"] is not None:
                return json.dumps(data["structured_output"])
            return str(data.get("response", ""))
        except json.JSONDecodeError:
            return stdout.strip()

    def ask(
        self,
        prompt: str,
        *,
        format: str = "text",
        schema: Any = None,
        temperature: float | None = None,
        thinking: bool | None = None,
    ) -> Any:
        cmd = self._build_cmd(prompt, format, schema, thinking)

        try:
            res = subprocess.run(
                cmd,
                stdin=subprocess.DEVNULL,
                capture_output=True,
                text=True,
                check=False,
            )
        except Exception as e:
            raise ExecutionError(f"Failed to execute agy CLI: {e}") from e

        if res.returncode != 0 and not res.stdout:
            raise ExecutionError(f"agy CLI exited with code {res.returncode}: {res.stderr.strip()}")

        result_str = self._parse_output(res.stdout)
        if schema is not None:
            return validate_schema_output(schema, result_str)
        if format == "json":
            return _strip_markdown_fence(result_str)

        return result_str
