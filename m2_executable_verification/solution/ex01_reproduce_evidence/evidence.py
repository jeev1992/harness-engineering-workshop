"""Module 2 exercise — reproduce recorded evidence (reference solution).

Check: python m2_executable_verification/exercises/check.py --solution
"""

from __future__ import annotations

import ast
from collections.abc import Callable


def reproduce(feature: dict, execute: Callable[[str], tuple[int, str]]) -> dict:
    """Re-execute recorded evidence and report whether it reproduces."""
    evidence = feature.get("evidence", {})
    exit_code, observed = execute(str(evidence.get("command", "")))
    return {
        "passed": exit_code == 0 and observed == evidence.get("observed"),
        "exit": exit_code,
        "observed": observed,
    }


# Stretch: a structural lint. It is a sensor that reads the code itself, before
# anything runs, and says how to fix what it finds.


def lint_derived_state(source: str) -> list[str]:
    """Return one message per function that deletes a source file but never updates the index.

    A function "deletes a source file" when it calls `.unlink()`, and "updates the
    index" when it calls `_write_index(...)`. Each message starts with the
    function's name followed by "()" and must say how to fix it (mention
    `_write_index`), because the reader may be an agent. Sort the messages;
    return [] when the source is clean.
    """
    messages = []
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        called = [call.func for call in ast.walk(node) if isinstance(call, ast.Call)]
        unlinks = any(isinstance(func, ast.Attribute) and func.attr == "unlink" for func in called)
        writes_index = any(isinstance(func, ast.Name) and func.id == "_write_index" for func in called)
        if unlinks and not writes_index:
            messages.append(
                f"{node.name}() deletes a source file but never updates the index. "
                f"Fix: call _write_index(...) in {node.name}() after removing the file; "
                "the index is the system of record for listing and answering."
            )
    return sorted(messages)
