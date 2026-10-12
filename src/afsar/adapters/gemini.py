"""Google Gemini REST API adapter using standard library urllib."""

import json
import os
import urllib.error
import urllib.request
from typing import Any

from afsar.adapters.base import BaseAdapter
from afsar.exceptions import ExecutionError
from afsar.schema import _strip_markdown_fence, to_json_schema, validate_schema_output


class GeminiAdapter(BaseAdapter):
    """Adapter for Google Gemini REST API."""

    name = "gemini"
    supports_tools = False
    supports_thinking = True
    supports_schema = True

    def __init__(self, model: str | None = None, api_key: str | None = None) -> None:
        self.model = model or "gemini-2.0-flash"
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Gemini API key is required. Set GEMINI_API_KEY or pass api_key.")

    def ask(
        self,
        prompt: str,
        *,
        format: str = "text",
        schema: Any = None,
        temperature: float | None = None,
        thinking: bool | None = None,
    ) -> Any:
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
            f"?key={self.api_key}"
        )

        gen_config: dict[str, Any] = {}
        if temperature is not None:
            gen_config["temperature"] = temperature

        if schema is not None:
            gen_config["responseMimeType"] = "application/json"
            gen_config["responseSchema"] = to_json_schema(schema)
        elif format == "json":
            gen_config["responseMimeType"] = "application/json"

        payload: dict[str, Any] = {
            "contents": [{"parts": [{"text": prompt}]}],
        }
        if gen_config:
            payload["generationConfig"] = gen_config

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8", errors="replace")
            raise ExecutionError(f"Gemini API error ({e.code}): {error_body}") from e
        except Exception as e:
            raise ExecutionError(f"Failed to communicate with Gemini API: {e}") from e

        try:
            candidates = data.get("candidates", [])
            parts = candidates[0].get("content", {}).get("parts", [])
            result_str = parts[0].get("text", "")
        except (IndexError, KeyError) as e:
            raise ExecutionError(f"Unexpected response structure from Gemini API: {data}") from e

        if schema is not None:
            return validate_schema_output(schema, result_str)
        if format == "json":
            return _strip_markdown_fence(result_str)

        return result_str
