"""Inspector script evaluating examples/teach_literals.py using afsar.

Demonstrates:
1. Setting up afsar: afsar.setup()
2. Asking afsar (an agent with command and file tools) to run an external script 5 times.
3. Reviewing source code and assessing topic coverage and potential bugs.
"""

from pathlib import Path

import afsar


def inspect_literals(script_path: str = "examples/teach_literals.py") -> str:
    """Use afsar to run and analyze teach_literals.py for coverage and issues."""
    path = Path(script_path)
    code_snippet = ""
    if path.exists():
        code_snippet = (
            f"\n\nSource code of `{script_path}`:\n```python\n"
            f"{path.read_text(encoding='utf-8')}\n```"
        )

    prompt = (
        f"You are a Python instructor and code reviewer.\n"
        f"Please inspect `{script_path}`:\n"
        f"1. Run `{script_path}` 5 times using your bash/command tool (pass sample answers via stdin, e.g. `echo \"0x10\" | python {script_path}`).\n"
        f"2. Review the code to assess whether it provides good coverage of the topic 'literals' in Python.\n"
        f"3. Identify any bugs, prompt injection vulnerabilities, or behavioral issues.\n"
        f"4. Provide a clear summary with coverage assessment and recommendations."
        f"{code_snippet}"
    )

    return afsar.ask(prompt)


def main() -> None:
    """Run the inspection."""
    afsar.setup()
    print("--- Inspecting teach_literals.py with afsar ---\n")
    report = inspect_literals()
    print(report)


if __name__ == "__main__":
    main()
