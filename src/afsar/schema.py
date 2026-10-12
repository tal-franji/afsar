"""Schema extraction and validation helpers without mandatory dependencies."""

import dataclasses
import json
from collections.abc import Sequence
from typing import Any, cast, get_type_hints


def is_pydantic_model(cls: Any) -> bool:
    """Check if cls is a Pydantic model class without importing pydantic at module load."""
    return isinstance(cls, type) and (
        hasattr(cls, "model_json_schema") or hasattr(cls, "parse_raw")
    )


def _infer_type_string(field_type: Any) -> str:
    """Map a Python type to a JSON schema type string."""
    if field_type in (int, float):
        return "number" if field_type is float else "integer"
    if field_type is bool:
        return "boolean"
    if getattr(field_type, "__origin__", None) in (list, Sequence):
        return "array"
    return "string"


def _dataclass_to_json_schema(schema_cls: Any) -> dict[str, Any]:
    """Convert a dataclass to a JSON schema dict."""
    properties: dict[str, Any] = {}
    required: list[str] = []
    try:
        type_hints = get_type_hints(schema_cls)
    except Exception:
        type_hints = {}

    for f in dataclasses.fields(schema_cls):
        field_type = type_hints.get(f.name, f.type)
        properties[f.name] = {"type": _infer_type_string(field_type)}
        if f.default is dataclasses.MISSING and f.default_factory is dataclasses.MISSING:
            required.append(f.name)

    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }


def to_json_schema(schema_cls: Any) -> dict[str, Any]:
    """Convert a schema class (Pydantic, dataclass, or dict) to a standard JSON schema dict."""
    if isinstance(schema_cls, dict):
        return schema_cls

    if is_pydantic_model(schema_cls):
        if hasattr(schema_cls, "model_json_schema"):
            return cast(dict[str, Any], schema_cls.model_json_schema())
        if hasattr(schema_cls, "schema"):
            return cast(dict[str, Any], schema_cls.schema())

    if dataclasses.is_dataclass(schema_cls):
        return _dataclass_to_json_schema(schema_cls)

    raise TypeError(
        f"Unsupported schema type '{schema_cls}'. Pass a Pydantic model, @dataclass, or JSON schema dict."
    )


def _strip_markdown_fence(raw_text: str) -> str:
    """Strip markdown code fence blocks (```json ... ```) if present."""
    cleaned = raw_text.strip()
    if "```json" in cleaned:
        cleaned = cleaned.split("```json", 1)[1].split("```", 1)[0].strip()
    elif "```" in cleaned:
        cleaned = cleaned.split("```", 1)[1].split("```", 1)[0].strip()

    try:
        json.loads(cleaned)
        return cleaned
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end > start:
            candidate = cleaned[start : end + 1]
            try:
                json.loads(candidate)
                return candidate
            except json.JSONDecodeError:
                pass
    return cleaned


def validate_schema_output(schema_cls: Any, raw_json_str: str) -> Any:
    """Validate and instantiate the target schema class from a raw JSON string."""
    cleaned = _strip_markdown_fence(raw_json_str)

    if is_pydantic_model(schema_cls):
        if hasattr(schema_cls, "model_validate_json"):
            return schema_cls.model_validate_json(cleaned)
        if hasattr(schema_cls, "parse_raw"):
            return schema_cls.parse_raw(cleaned)

    parsed = json.loads(cleaned)
    if dataclasses.is_dataclass(schema_cls):
        cls_factory = cast(Any, schema_cls)
        if isinstance(parsed, dict):
            field_names = {f.name for f in dataclasses.fields(schema_cls)}
            filtered = {k: v for k, v in parsed.items() if k in field_names}
            return cls_factory(**filtered)
        return cls_factory(**parsed)

    return parsed
