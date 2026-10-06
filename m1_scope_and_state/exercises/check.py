"""
Check — Module 1, Exercise 1: the scope gate
============================================
Runs the contract cases against your assess_scope() and checks the
feature_list.json and plan.json in this folder.

Run:
    python m1_scope_and_state/exercises/check.py              # your work
    python m1_scope_and_state/exercises/check.py --stretch    # optional stretch
    python m1_scope_and_state/exercises/check.py --solution   # the reference solution
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from m1_scope_and_state.rules import validate_features, validate_plan
from shared.checks import Check, contract_check, guarded, load_exercise, run_check_cli

EXERCISE_DIR = Path(__file__).resolve().parent
SOLUTION_DIR = EXERCISE_DIR.parent / "solution" / "ex01_scope_gate"
CODE = "scope_gate.py"
EDIT = [CODE, "feature_list.json", "plan.json"]
# A fresh checkout must fail on exactly these checks, and the solution on none.
STARTER_FAILS_WITH = {"scope-function-contract", "wip-limit", "scope-declared", "next-action-bounded"}


def check_function(base: Path) -> Check:
    module = load_exercise(base / CODE)
    cases = [
        (
            [{"id": "delete", "status": "not-started"}],
            {"allowed_paths": ["kb/kb.py"], "next_action": "Select the delete feature"},
            {"wip-limit": True, "scope-declared": True, "next-action-bounded": True},
        ),
        (
            [{"id": "delete", "status": "in-progress"}],
            {"allowed_paths": ["kb/kb.py"], "next_action": "Implement delete"},
            {"wip-limit": True, "scope-declared": True, "next-action-bounded": True},
        ),
        (
            [
                {"id": "delete", "status": "in-progress"},
                {"id": "retrieval", "status": "in-progress"},
            ],
            {"allowed_paths": ["kb/kb.py"], "next_action": "Implement delete"},
            {"wip-limit": False, "scope-declared": True, "next-action-bounded": True},
        ),
        (
            [{"id": "delete", "status": "in-progress"}],
            {"allowed_paths": [], "next_action": ""},
            {"wip-limit": True, "scope-declared": False, "next-action-bounded": False},
        ),
    ]
    results = [module.assess_scope(features, plan) for features, plan, _ in cases]
    return contract_check("scope-function-contract", results, [case[2] for case in cases])


def check(base: Path) -> list[Check]:
    return [
        guarded("scope-function-contract", lambda: check_function(base)),
        *validate_features(base / "feature_list.json"),
        *validate_plan(base / "plan.json"),
    ]


def check_stretch_function(base: Path) -> Check:
    module = load_exercise(base / CODE)
    cases = [
        (["kb/kb.py", "tests/"], ["kb/kb.py", "tests/test_kb.py"], []),
        (["kb/kb.py"], ["kb\\kb.py", "./config/rogue.md"], ["config/rogue.md"]),
        (["tests/"], ["tests_extra/test_x.py", "tests/unit/test_y.py"], ["tests_extra/test_x.py"]),
        ([], ["kb/kb.py"], ["kb/kb.py"]),
        (["kb/kb.py"], ["z.md", "a.md", "kb/kb.py"], ["a.md", "z.md"]),
    ]
    results = [module.scope_violations(allowed, changed) for allowed, changed, _ in cases]
    return contract_check("stretch:scope-violations", results, [case[2] for case in cases])


def check_stretch(base: Path) -> list[Check]:
    return [guarded("stretch:scope-violations", lambda: check_stretch_function(base))]


if __name__ == "__main__":
    run_check_cli(
        exercise_dir=EXERCISE_DIR,
        solution_dir=SOLUTION_DIR,
        edit=EDIT,
        check=check,
        check_stretch=check_stretch,
    )
