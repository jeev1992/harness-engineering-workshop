"""Module 1 harness rules: feature state is explicit and work is bounded.

These are the reference implementations the rest of the workshop builds on.
"""

from __future__ import annotations

from pathlib import Path

from shared.checks import Check, load_json

STATUSES = {"not-started", "in-progress", "blocked", "passing"}


def validate_features(path: Path) -> list[Check]:
    """Known statuses, at most one feature in progress, and evidence on every passing feature."""
    features = load_json(path)
    checks: list[Check] = []
    invalid = [item["id"] for item in features if item.get("status") not in STATUSES]
    checks.append(
        Check(
            "known-statuses",
            not invalid,
            f"invalid: {', '.join(invalid) or 'none'}",
            fix=f"use one of: {', '.join(sorted(STATUSES))}",
        )
    )
    active = [item["id"] for item in features if item.get("status") == "in-progress"]
    checks.append(
        Check(
            "wip-limit",
            len(active) <= 1,
            f"in-progress: {', '.join(active) or 'none'}",
            fix="finish or park all but one: set the others back to not-started in feature_list.json",
        )
    )
    missing = [
        item["id"]
        for item in features
        if item.get("status") == "passing"
        and not all(str(item.get("evidence", {}).get(key, "")).strip() for key in ("command", "observed"))
    ]
    checks.append(
        Check(
            "passing-has-evidence",
            not missing,
            f"missing evidence: {', '.join(missing) or 'none'}",
            fix="run a verification command and record its command and real observed output, "
            "or set the status back to in-progress",
        )
    )
    return checks


def validate_plan(path: Path) -> list[Check]:
    """A plan declares a non-empty scope and a bounded next action."""
    plan = load_json(path)
    allowed = plan.get("allowed_paths", [])
    return [
        Check(
            "scope-declared",
            bool(allowed) and all(isinstance(item, str) and item.strip() for item in allowed),
            f"allowed paths: {', '.join(allowed) or 'none'}",
            fix='list every path this work may change in plan.json "allowed_paths" before editing',
        ),
        Check(
            "next-action-bounded",
            bool(str(plan.get("next_action", "")).strip()),
            f"next action: {plan.get('next_action') or 'none'}",
            fix='write one concrete, checkable next step in plan.json "next_action"',
        ),
    ]


def scope_violations(allowed_paths: list[str], changed_paths: list[str]) -> list[str]:
    """Changed paths outside the declared scope (the reference for the Module 1 stretch)."""

    def normalize(path: str) -> str:
        path = path.replace("\\", "/")
        while path.startswith("./"):
            path = path[2:]
        return path

    allowed = [normalize(path) for path in allowed_paths]
    changed = {normalize(path) for path in changed_paths}
    return sorted(
        path
        for path in changed
        if not any(
            path == entry or (entry.endswith("/") and path.startswith(entry)) for entry in allowed
        )
    )
