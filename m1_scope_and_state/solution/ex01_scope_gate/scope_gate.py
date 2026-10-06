"""Module 1 exercise — the scope gate (reference solution).

Check: python m1_scope_and_state/exercises/check.py --solution
"""

from __future__ import annotations


def assess_scope(features: list[dict], plan: dict) -> dict[str, bool]:
    """Return the three scope predicates for the current work state."""
    active = [feature for feature in features if feature["status"] == "in-progress"]
    allowed_paths = plan.get("allowed_paths", [])
    next_action = str(plan.get("next_action", "")).strip()
    return {
        "wip-limit": len(active) <= 1,
        "scope-declared": bool(allowed_paths)
        and all(isinstance(path, str) and path.strip() for path in allowed_paths),
        "next-action-bounded": bool(next_action),
    }


# Stretch: compare declared scope with the paths a change actually touched.


def _normalize_path(path: str) -> str:
    path = path.replace("\\", "/")
    while path.startswith("./"):
        path = path[2:]
    return path


def scope_violations(allowed_paths: list[str], changed_paths: list[str]) -> list[str]:
    """Return the sorted changed paths that fall outside the declared scope.

    An allowed entry ending in "/" covers everything beneath that directory.
    Treat backslashes as "/" and ignore a leading "./".
    """
    allowed = [_normalize_path(path) for path in allowed_paths]

    def covered(path: str) -> bool:
        return any(
            path == entry or (entry.endswith("/") and path.startswith(entry))
            for entry in allowed
        )

    changed = {_normalize_path(path) for path in changed_paths}
    return sorted(path for path in changed if not covered(path))
