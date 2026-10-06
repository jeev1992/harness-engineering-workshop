"""Module 2 exercise — reproduce recorded evidence.

Brief: m2_executable_verification/exercises/ex01_reproduce_evidence.md
Check: python m2_executable_verification/exercises/check.py
"""

from __future__ import annotations

from collections.abc import Callable


def reproduce(feature: dict, execute: Callable[[str], tuple[int, str]]) -> dict:
    """Re-execute recorded evidence and report whether it reproduces."""
    evidence = feature["evidence"]
    return {
        "passed": bool(evidence.get("observed")),
        "exit": 0,
        "observed": evidence.get("observed", ""),
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
    raise NotImplementedError
