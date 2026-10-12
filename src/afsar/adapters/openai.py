"""OpenAI REST API adapter using standard library urllib."""

import json
import os
import urllib.error
import urllib.request
from typing import Any

from afsar.adapters.base import BaseAdapter
from afsar.exceptions import ExecutionError
from afsar.schema import _strip_markdown_fence, to_json_schema, validate_schema_output


class OpenAIAdapter(BaseAdapter):
    """Adapter for OpenAI Chat Completions REST API."""

    name = "openai"
    supports_tools = False
    supports_thinking = True
    supports_schema = True

    def __init__(self, model: str | None = None, api_key: str | None = None) -> None:
        self.model = model or "gpt-4o-mini"
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY or pass api_key.")

    def ask(
        self,
        prompt: str,
        *,
        format: str = "text",
        schema: Any = None,
        temperature: float | None = None,
        thinking: bool | None = None,
    ) -> Any:
        url = "https://api.openai.com/v1/chat/completions"

        payload: dict[str, Any] = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
        }
        if temperature is not None:
            payload["temperature"] = temperature

        if schema is not None:
            schema_dict = to_json_schema(schema)
            payload["response_format"] = {
                "type": "json_schema",
                "json_schema": {
                    "name": getattr(schema, "__name__", "ResponseSchema"),
                    "strict": False,
                    "schema": schema_dict,
                },
            }
        elif format == "json":
            payload["response_format"] = {"type": "json_object"}

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8", errors="replace")
            raise ExecutionError(f"OpenAI API error ({e.code}): {error_body}") from e
        except Exception as e:
            raise ExecutionError(f"Failed to communicate with OpenAI API: {e}") from e

        try:
            choices = data.get("choices", [])
            result_str = choices[0].get("message", {}).get("content", "")
        except (IndexError, KeyError) as e:
            raise ExecutionError(f"Unexpected response structure from OpenAI API: {data}") from e

        if schema is not None:
            return validate_schema_output(schema, result_str)
        if format == "json":
            return _strip_markdown_fence(result_str)

        return result_str
