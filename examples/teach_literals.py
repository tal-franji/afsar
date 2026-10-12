"""Interactive Python literal quiz for students using afsar.

Demonstrates:
1. Setting up afsar: afsar.setup()
2. Call 1: Asking the LLM with a high temperature to generate a quiz question.
3. Getting user input: input()
4. Call 2: Asking the LLM to test and explain the student's answer using a script template.
"""

import afsar


def ask_quiz_question() -> str:
    """Generate a question testing knowledge of Python literals."""
    prompt = """You are a Python instructor. Create ONE quiz question asking a student to write a Python literal.
Choose from:
- Integers (hexadecimal 0x..., octal 0o..., binary 0b..., or with underscores 1_000_000)
- Floats (standard float or scientific notation like 1e-4)
- Strings (single, double, triple quotes, raw strings r"...", byte literals b"...")

Requirements:
- Ask the student to write only the literal itself.
- Do NOT include the answer or spoilers. Output ONLY the question."""

    return str(afsar.ask(prompt, temperature=0.9))


def evaluate_answer(question: str, user_answer: str) -> str:
    """Evaluate student's answer using a Python script template."""
    eval_prompt = f"""You are a Python instructor evaluating a student's answer.

Question:
{question}

Student Answer:
{user_answer}

Verification Script Template:
```python
value = {user_answer}
print(value)
```

Please test and evaluate the student's answer:
1. Is it a valid Python literal?
2. Does it correctly answer the question?
3. State whether it is CORRECT or INCORRECT.
4. If incorrect, explain the mistake and show the correct literal.
5. If correct, briefly explain how Python interprets it."""

    return str(afsar.ask(eval_prompt))


def main() -> None:
    """Run the interactive quiz."""
    afsar.setup()

    print("--- Python Literals Quiz ---\n")
    question = ask_quiz_question()
    print(question)

    user_answer = input("\nYour answer: ").strip()
    if not user_answer:
        print("No answer provided.")
        return

    print("\nChecking your answer...\n")
    feedback = evaluate_answer(question, user_answer)
    print(feedback)


if __name__ == "__main__":
    main()
