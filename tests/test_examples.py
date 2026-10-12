"""Tests for self-contained examples, including teach_literals."""

from unittest.mock import patch

from examples.teach_literals import (
    ask_quiz_question,
    evaluate_answer,
    main,
)


def test_ask_quiz_question_calls_ask_with_temperature() -> None:
    """ask_quiz_question should call afsar.ask with high temperature."""
    with patch("afsar.ask", return_value="Write a binary literal for 10.") as mock_ask:
        question = ask_quiz_question()
        assert question == "Write a binary literal for 10."
        mock_ask.assert_called_once()
        _, kwargs = mock_ask.call_args
        assert kwargs.get("temperature") is not None
        assert kwargs["temperature"] >= 0.8


def test_evaluate_answer_includes_template() -> None:
    """evaluate_answer should include original question and template snippet."""
    with patch("afsar.ask", return_value="CORRECT!") as mock_ask:
        feedback = evaluate_answer("Write hex for 16", "0x10")
        assert feedback == "CORRECT!"
        mock_ask.assert_called_once()
        prompt = mock_ask.call_args[0][0]
        assert "Write hex for 16" in prompt
        assert "value = 0x10" in prompt
        assert "print(value)" in prompt


def test_main_quiz_flow() -> None:
    """main should execute the setup, question generation, input, and evaluation."""
    with (
        patch("afsar.setup"),
        patch(
            "afsar.ask",
            side_effect=[
                "Write one million using underscores.",
                "CORRECT: underscores improve readability in Python.",
            ],
        ) as mock_ask,
        patch("builtins.input", return_value="1_000_000"),
    ):
        main()
        assert mock_ask.call_count == 2
