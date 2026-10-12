<p align="center">
  <img src="src/afsar/resources/afsar.png" alt="afsar logo" width="180" />
</p>

# afsar

A simple, student-friendly procedural Python library providing a uniform interface to LLMs. `afsar` prioritizes installed local coding agents (`claude-code`, `antigravity`) so students can use their existing agents and tools, and smoothly falls back to remote cloud APIs (`Gemini`, `OpenAI`).

- **Zero Mandatory Dependencies**: Built entirely with standard library tools (`dataclasses`, `urllib`). No heavy frameworks or Pydantic required.
- **Pure Procedural API**: Beginner-friendly `afsar.setup()` and `afsar.ask()`.
- **Built-in Local Tools**: Local agents default to `tools=["python", "files"]`, enabling students to write programs that ask LLMs to generate, run, and test code.
- **Typed Schemas**: Deserializes directly into Python's built-in `@dataclass` without third-party validation libraries.

---

## Installation

Install via pip:

```bash
pip install afsar
```

---

## Quickstart

### 1. Basic Text Query

```python
import afsar

# Setup is explicit and required once before asking
afsar.setup()

answer = afsar.ask("How do you define a function in Python?")
print(answer)
```

### 2. Structured Output with `@dataclass`

You don't need Pydantic to get typed objects. Standard Python dataclasses work out of the box:

```python
from dataclasses import dataclass
import afsar


@dataclass
class QuizQuestion:
    question: str
    points: int
    topic: str


afsar.setup()
quiz = afsar.ask("Create a beginner Python question.", schema=QuizQuestion)

print(quiz.question)
print(f"Points: {quiz.points}")
print(f"Topic: {quiz.topic}")
```

### 3. Raw JSON Output

If you just want a JSON-formatted string:

```python
import afsar

afsar.setup()
raw_json = afsar.ask("List 3 Python data structures.", format="json")
print(raw_json)  # Returns clean JSON string
```

### 4. Student Coding Exercises (Local Tools)

When using local agents (`claude` or `agy`), `afsar` defaults to `tools=["python", "files"]`. This allows asking the agent to write and test code locally:

```python
import afsar

afsar.setup()
response = afsar.ask(
    "Write a solution to check if a word is a palindrome, save it to palindrome.py, run it with python, and show the result."
)
print(response)
```

---

## Remote APIs (Gemini & OpenAI)

Remote models do not support local file or execution tools. When connecting to remote APIs, explicitly pass `tools=[]`:

```python
import afsar

# Using Gemini
afsar.setup(provider="gemini", api_key="YOUR_GEMINI_KEY", tools=[])

# Or using OpenAI
afsar.setup(provider="openai", api_key="YOUR_OPENAI_KEY", tools=[])

answer = afsar.ask("Explain recursion in simple terms.")
print(answer)
```

---

## Auto-Detection & Priority

Calling `afsar.setup()` without arguments automatically searches for available providers in this order:

1. **Claude Code CLI** (`claude`) in `PATH`
2. **Antigravity CLI** (`agy`) in `PATH`
3. **Google Gemini** (`GEMINI_API_KEY` in environment)
4. **OpenAI** (`OPENAI_API_KEY` in environment)

You can override the provider explicitly in code:

```python
afsar.setup(provider="agy")
```

Or via the `AFSAR_PROVIDER` environment variable:

```bash
export AFSAR_PROVIDER=agy
```

---

## Exceptions

- `NotSetupError`: Raised if `afsar.ask()` is called before `afsar.setup()`.
- `UnsupportedFeatureError`: Raised if requesting local tools (`tools=["python", "files"]`) on remote API providers.
- `ModelNotFoundError`: Raised if no supported local CLI or remote API key is discovered.
- `ExecutionError`: Raised if a CLI command or remote API request fails.
