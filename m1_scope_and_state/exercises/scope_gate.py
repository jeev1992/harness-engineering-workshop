"""Module 1 exercise — the scope gate.

Brief: m1_scope_and_state/exercises/ex01_scope_gate.md
Check: python m1_scope_and_state/exercises/check.py
"""

from __future__ import annotations


def assess_scope(features: list[dict], plan: dict) -> dict[str, bool]:
    """Return the three scope predicates for the current work state."""
    active = [feature for feature in features if feature["status"] == "in-progress"]
    return {
        "wip-limit": bool(active),
        "scope-declared": "allowed_paths" in plan,
        "next-action-bounded": "next_action" in plan,
    }


# Stretch: compare declared scope with the paths a change actually touched.


def scope_violations(allowed_paths: list[str], changed_paths: list[str]) -> list[str]:
    """Return the sorted changed paths that fall outside the declared scope.

    An allowed entry ending in "/" covers everything beneath that directory.
    Treat backslashes as "/" and ignore a leading "./".
    """
    raise NotImplementedError
