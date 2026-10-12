"""Checks that Python modules and functions do not exceed maximum line limits."""

import argparse
import ast
import sys
from pathlib import Path


def check_file(
    filepath: Path,
    max_module_lines: int,
    max_function_lines: int,
) -> list[str]:
    errors: list[str] = []
    try:
        content = filepath.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return [f"Could not read {filepath}: {e}"]

    lines = content.splitlines()
    line_count = len(lines)
    if line_count > max_module_lines:
        errors.append(
            f"[MODULE SIZE] {filepath}: {line_count} lines (max allowed: {max_module_lines})"
        )

    try:
        tree = ast.parse(content, filename=str(filepath))
    except Exception as e:
        errors.append(f"[SYNTAX ERROR] Could not parse AST for {filepath}: {e}")
        return errors

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            end_line = getattr(node, "end_lineno", node.lineno)
            func_len = end_line - node.lineno + 1
            if func_len > max_function_lines:
                errors.append(
                    f"[FUNCTION LENGTH] {filepath}:{node.lineno} function '{node.name}' is {func_len} lines (max allowed: {max_function_lines})"
                )

    return errors


def _collect_target_files(paths: list[str]) -> list[Path]:
    target_files: list[Path] = []
    if paths:
        for p in paths:
            path_obj = Path(p)
            if path_obj.is_file() and path_obj.suffix == ".py":
                target_files.append(path_obj)
            elif path_obj.is_dir():
                target_files.extend(path_obj.rglob("*.py"))
    else:
        for root in ["src", "ops", "tests"]:
            root_path = Path(root)
            if root_path.is_dir():
                target_files.extend(root_path.rglob("*.py"))

    skip_patterns = {
        ".venv",
        "venv",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "build",
    }
    return [
        f for f in sorted(set(target_files)) if not any(pat in f.parts for pat in skip_patterns)
    ]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Enforce module size and function length limits on Python code."
    )
    parser.add_argument(
        "--max-module-lines",
        type=int,
        default=600,
        help="Maximum lines allowed per module (default: 600)",
    )
    parser.add_argument(
        "--max-function-lines",
        type=int,
        default=220,
        help="Maximum lines allowed per function (default: 220)",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help="Files or directories to inspect. If empty, scans src, ops, and tests.",
    )

    args = parser.parse_args()
    filtered_files = _collect_target_files(args.paths)

    all_errors: list[str] = []
    for f in filtered_files:
        errors = check_file(f, args.max_module_lines, args.max_function_lines)
        all_errors.extend(errors)

    if all_errors:
        print("=" * 70, file=sys.stderr)
        print("CODE SIZE LIMIT VIOLATIONS DETECTED:", file=sys.stderr)
        for err in all_errors:
            print(f"  - {err}", file=sys.stderr)
        print("=" * 70, file=sys.stderr)
        return 1

    print(
        f"All {len(filtered_files)} Python modules meet limits (<= {args.max_module_lines} lines/module, <= {args.max_function_lines} lines/function)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
