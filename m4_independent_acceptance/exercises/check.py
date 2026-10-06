"""
Check — Module 4, Exercise 1: enforce the plan
==============================================
Two things are checked, because a guard is only as good as its tests:

    guard-function-contract   your decide() against cases you can't see
    cases-both-directions     guard_cases.json has cases that must BLOCK and
                              cases that must ALLOW (at least 3 of each)
    cases-agree-with-reference  every expectation in guard_cases.json is right
    cases-catch-mutants       each deliberately broken guard fails at least one
                              of your cases (mutation testing your tests)

Run:
    python m4_independent_acceptance/exercises/check.py              # your work
    python m4_independent_acceptance/exercises/check.py --stretch    # optional stretch
    python m4_independent_acceptance/exercises/check.py --solution   # the reference solution
"""

from __future__ import annotations

import os
import sys
import tempfile
from collections.abc import Callable
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from m1_scope_and_state.hooks.scope_guard import ALLOW, BLOCK, EDIT_TOOLS, _relative, judge
from shared.checks import Check, contract_check, guarded, load_exercise, load_json, run_check_cli
from shared.project import STATE_FILES

EXERCISE_DIR = Path(__file__).resolve().parent
SOLUTION_DIR = EXERCISE_DIR.parent / "solution" / "ex01_enforce_the_plan"
CODE = "guard.py"
CASES = "guard_cases.json"
EDIT = [CODE, CASES]
# A fresh checkout must fail on exactly these checks, and the solution on none.
STARTER_FAILS_WITH = {"guard-function-contract", "cases-both-directions", "cases-catch-mutants"}

PROJECT = os.path.join(tempfile.gettempdir(), "workshop-guard-project")  # never touched: decide() is pure
PLAN = {"allowed_paths": ["kb/kb.py", "kb/test_kb.py", "docs/"]}
Guard = Callable[[dict, str, "dict | None"], tuple[int, str]]


def event_for(case: dict) -> dict:
    tool_input = (
        {"command": case["command"]} if "command" in case
        else {"file_path": os.path.join(PROJECT, *str(case["path"]).split("/"))}
    )
    return {"hook_event_name": "PreToolUse", "tool_name": case["tool"], "tool_input": tool_input}


def plan_for(case: dict) -> dict | None:
    return case["plan"] if "plan" in case else PLAN


def _is_state_edit(event: dict) -> bool:
    if event.get("tool_name") not in EDIT_TOOLS:
        return False
    relative = _relative(str(event["tool_input"].get("file_path", "")), Path(PROJECT))
    return relative in STATE_FILES


def _prefix_match(event: dict, project: str, plan: dict | None) -> tuple[int, str]:
    relative = _relative(str(event.get("tool_input", {}).get("file_path", "")), Path(project))
    if event.get("tool_name") in EDIT_TOOLS and plan and relative and relative != "plan.json":
        if any(relative.startswith(entry.rstrip("/")) for entry in plan.get("allowed_paths", [])):
            return ALLOW, ""
    return judge(event, project, plan)


# Each mutant is a plausible bug, and the kind of case that catches it.
MUTANTS: dict[str, tuple[Guard, str]] = {
    "allows everything": (lambda e, p, plan: (ALLOW, ""), "add cases the guard must block"),
    "blocks everything": (
        lambda e, p, plan: (BLOCK, "Blocked: everything"),
        "add cases the guard must allow, such as an in-scope edit",
    ),
    "blocks tools that don't edit": (
        lambda e, p, plan: (BLOCK, "Blocked") if e.get("tool_name") not in EDIT_TOOLS else judge(e, p, plan),
        "add an allow case for a tool that doesn't edit, such as Read or Bash",
    ),
    "no exemption for state files": (
        lambda e, p, plan: (BLOCK, "Blocked") if _is_state_edit(e) else judge(e, p, plan),
        "add an allow case for feature_list.json or session-handoff.md",
    ),
    "matches paths by prefix": (
        _prefix_match,
        "add a block case for a path that only shares a prefix, such as kb/kb.py.bak or docs_extra/",
    ),
}


def verdict(guard: Guard, case: dict) -> str:
    return "allow" if guard(event_for(case), PROJECT, plan_for(case))[0] == ALLOW else "block"


def check_function(base: Path) -> Check:
    decide = load_exercise(base / CODE).decide
    cases = [
        {"tool": "Edit", "path": "kb/kb.py"},
        {"tool": "Write", "path": "kb/test_kb.py"},
        {"tool": "Write", "path": "docs/a/b.md"},
        {"tool": "Write", "path": "session-handoff.md"},
        {"tool": "Read", "path": "config/secret.md"},
        {"tool": "Bash", "command": "echo x > notes.md"},
        {"tool": "Write", "path": "config/retrieval-notes.md"},
        {"tool": "Edit", "path": "plan.json"},
        {"tool": "Write", "path": "kb/kb.py.bak"},
        {"tool": "Write", "path": "docs_extra/a.md"},
        {"tool": "Write", "path": "kb/../config/x.md"},
        {"tool": "Write", "path": "../outside.txt"},
        {"tool": "Edit", "path": "kb/kb.py", "plan": None},
    ]
    results, expected = [], []
    for case in cases:
        code, message = decide(event_for(case), PROJECT, plan_for(case))
        results.append((code, message.startswith("Blocked:") if code == BLOCK else message == ""))
        expected.append((judge(event_for(case), PROJECT, plan_for(case))[0], True))
    return contract_check("guard-function-contract", results, expected)


def _load_cases(base: Path) -> list[dict]:
    cases = load_json(base / CASES)
    for index, case in enumerate(cases, 1):
        if case.get("expect") not in ("allow", "block") or "tool" not in case or not ({"path", "command"} & set(case)):
            raise ValueError(f'case {index} needs "tool", "path" or "command", and "expect": "allow" or "block"')
    return cases


def check_cases(base: Path) -> list[Check]:
    cases = _load_cases(base)
    blocks = sum(case["expect"] == "block" for case in cases)
    allows = len(cases) - blocks
    wrong = [case.get("label", f"case {index}") for index, case in enumerate(cases, 1) if verdict(judge, case) != case["expect"]]
    survivors = [
        (name, hint) for name, (mutant, hint) in MUTANTS.items()
        if all(verdict(mutant, case) == case["expect"] for case in cases)
    ]
    return [
        Check(
            "cases-both-directions", blocks >= 3 and allows >= 3, f"{blocks} must-block, {allows} must-allow",
            fix="a suite that only lists what to block can't notice a guard that blocks everything: "
            "add at least 3 cases the guard must allow",
        ),
        Check(
            "cases-agree-with-reference", not wrong, f"wrong expectation: {', '.join(wrong) or 'none'}",
            fix="re-read the rules in guard.py's docstring; these cases expect the wrong verdict",
        ),
        Check(
            "cases-catch-mutants", not survivors,
            f"broken guards your cases don't catch: {', '.join(name for name, _ in survivors) or 'none'}",
            fix="; ".join(hint for _, hint in survivors),
        ),
    ]


def check(base: Path) -> list[Check]:
    def cases_or_error() -> list[Check]:
        try:
            return check_cases(base)
        except Exception as error:
            return [Check("cases-both-directions", False, f"{type(error).__name__}: {error}", fix=f"fix {CASES}")]

    return [guarded("guard-function-contract", lambda: check_function(base)), *cases_or_error()]


def _event(turn: int, role: str, kind: str, **detail: object) -> dict[str, object]:
    return {"turn": turn, "role": role, "type": kind, **detail}


def check_stretch_function(base: Path) -> Check:
    module = load_exercise(base / CODE)

    def finding(turn: int, ident: str) -> dict:
        return _event(turn, "checker", "finding", id=ident)

    def fix(turn: int, ident: str) -> dict:
        return _event(turn, "maker", "fix", id=ident)

    def verification(turn: int, exit_code: int) -> dict:
        return _event(turn, "checker", "verification", command="kb list", exit=exit_code)

    cases = [
        ([finding(3, "a"), fix(4, "a"), verification(5, 0)], []),
        ([finding(3, "a")], ["a"]),
        ([finding(3, "a"), fix(4, "a"), verification(5, 1)], ["a"]),
        ([fix(2, "a"), finding(3, "a"), verification(4, 0)], ["a"]),
        ([finding(1, "a"), verification(2, 0), fix(3, "a")], ["a"]),
        ([finding(1, "b"), finding(2, "a"), fix(3, "a"), verification(4, 0)], ["b"]),
    ]
    results = [module.open_findings(events) for events, _ in cases]
    return contract_check("stretch:open-findings", results, [case[1] for case in cases])


def check_stretch(base: Path) -> list[Check]:
    return [guarded("stretch:open-findings", lambda: check_stretch_function(base))]


if __name__ == "__main__":
    run_check_cli(
        exercise_dir=EXERCISE_DIR,
        solution_dir=SOLUTION_DIR,
        edit=EDIT,
        check=check,
        check_stretch=check_stretch,
    )
