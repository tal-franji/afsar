"""Tests for schema handling and conversion with standard library tools."""

from dataclasses import dataclass

from afsar.schema import to_json_schema, validate_schema_output


@dataclass
class QuestionAnswer:
    question: str
    points: int
    topic: str = "general"


def test_dataclass_to_json_schema() -> None:
    """Standard dataclass should produce a valid JSON schema dictionary."""
    schema = to_json_schema(QuestionAnswer)
    assert schema["type"] == "object"
    assert "question" in schema["properties"]
    assert schema["properties"]["question"]["type"] == "string"
    assert "points" in schema["properties"]
    assert schema["properties"]["points"]["type"] == "integer"
    assert "question" in schema["required"]
    assert "points" in schema["required"]
    assert "topic" not in schema["required"]


def test_validate_schema_output_dataclass() -> None:
    """Raw JSON output should deserialize cleanly into a dataclass instance."""
    raw = '{"question": "What is Python?", "points": 10, "topic": "programming"}'
    obj = validate_schema_output(QuestionAnswer, raw)
    assert isinstance(obj, QuestionAnswer)
    assert obj.question == "What is Python?"
    assert obj.points == 10
    assert obj.topic == "programming"


def test_validate_schema_output_markdown_fence() -> None:
    """Markdown fences should be automatically stripped before validation."""
    raw = '```json\n{"question": "What is 1+1?", "points": 5}\n```'
    obj = validate_schema_output(QuestionAnswer, raw)
    assert isinstance(obj, QuestionAnswer)
    assert obj.question == "What is 1+1?"
    assert obj.points == 5


def test_validate_schema_output_extra_fields_ignored() -> None:
    """Extra fields in JSON should be safely ignored when hydrating a dataclass."""
    raw = '{"question": "What is 2+2?", "points": 4, "toolAction": "Done", "extra": 123}'
    obj = validate_schema_output(QuestionAnswer, raw)
    assert isinstance(obj, QuestionAnswer)
    assert obj.question == "What is 2+2?"
    assert obj.points == 4


def test_validate_schema_output_embedded_json() -> None:
    """JSON embedded within explanatory text should still parse."""
    raw = 'Here is the answer:\n{"question": "What is 3+3?", "points": 6}\nHope this helps!'
    obj = validate_schema_output(QuestionAnswer, raw)
    assert isinstance(obj, QuestionAnswer)
    assert obj.question == "What is 3+3?"
    assert obj.points == 6
