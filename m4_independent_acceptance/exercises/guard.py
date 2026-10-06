"""Module 4 exercise — enforce the plan: a scope guard and its tests.

Brief: m4_independent_acceptance/exercises/ex01_enforce_the_plan.md
Check: python m4_independent_acceptance/exercises/check.py
"""

from __future__ import annotations

import os

ALLOW, BLOCK = 0, 2  # Claude Code blocks a tool call only on exit code 2.
EDIT_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}
STATE_FILES = {"feature_list.json", "session-handoff.md"}


def decide(event: dict, project: str, plan: dict | None) -> tuple[int, str]:
    """Decide one Claude Code PreToolUse event. Return (ALLOW, "") or (BLOCK, reason).

    `event` is the JSON Claude Code sends: {"tool_name": ..., "tool_input": {"file_path": ...}}.
    `project` is the absolute project root. `plan` is plan.json as a dict, or None.
    The edited path is tool_input["file_path"] (absolute). Apply these rules in order:

    1. A tool that does not edit files (not in EDIT_TOOLS): allow.
    2. A path outside `project` (including via ".."): block.
    3. A STATE_FILES entry at the project root: allow.
    4. No plan (plan is None): block.
    5. plan.json itself: block. The maker may not widen its own scope.
    6. Inside plan["allowed_paths"] (the exact file, or anything under an entry
       ending in "/"): allow. "docs/" covers docs/a.md but not docs_extra/a.md.
    7. Anything else: block.

    Every blocking reason starts with "Blocked:" and tells the agent what to do instead.
    """
    path = str((event.get("tool_input") or {}).get("file_path", ""))
    allowed = (plan or {}).get("allowed_paths", [])
    if any(path.endswith(entry) for entry in allowed):  # the tempting shortcut
        return ALLOW, ""
    return BLOCK, "Blocked: outside the declared scope."


# Stretch: the findings-addressed rule from the capstone ladder.


def open_findings(events: list[dict]) -> list[str]:
    """Return the sorted ids of findings that are not closed.

    A finding is closed only by a later fix with the same id, followed by a
    passing (exit 0) verification after that fix.
    """
    raise NotImplementedError
