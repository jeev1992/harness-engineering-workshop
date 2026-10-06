"""Module 4 exercise — enforce the plan: a scope guard and its tests (reference solution).

Check: python m4_independent_acceptance/exercises/check.py --solution
"""

from __future__ import annotations

import os

ALLOW, BLOCK = 0, 2  # Claude Code blocks a tool call only on exit code 2.
EDIT_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}
STATE_FILES = {"feature_list.json", "session-handoff.md"}


def _inside(file_path: str, project: str) -> str | None:
    """The path relative to the project with "/" separators, or None when it is outside."""
    file = os.path.normcase(os.path.abspath(file_path))
    root = os.path.normcase(os.path.abspath(project))
    try:
        if os.path.commonpath([file, root]) != root:
            return None
    except ValueError:  # different drives on Windows
        return None
    return os.path.relpath(file, root).replace("\\", "/")


def _covered(relative: str, allowed: list[str]) -> bool:
    entries = [os.path.normcase(entry).replace("\\", "/") for entry in allowed]
    return any(relative == entry or (entry.endswith("/") and relative.startswith(entry)) for entry in entries)


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
    if event.get("tool_name") not in EDIT_TOOLS:
        return ALLOW, ""
    tool_input = event.get("tool_input") or {}
    file_path = str(tool_input.get("file_path") or tool_input.get("notebook_path") or "")
    relative = _inside(file_path, project)
    if relative is None:
        return BLOCK, f"Blocked: {file_path} is outside the project. Edit only files inside it."
    if relative in {os.path.normcase(name) for name in STATE_FILES}:
        return ALLOW, ""
    if plan is None:
        return BLOCK, "Blocked: no plan.json yet. A planner must declare allowed_paths first."
    if relative == os.path.normcase("plan.json"):
        return BLOCK, "Blocked: plan.json belongs to the planner. Ask for the plan to change instead."
    allowed = plan.get("allowed_paths", [])
    if _covered(relative, allowed):
        return ALLOW, ""
    return BLOCK, f"Blocked: {relative} is outside the declared scope ({', '.join(allowed)}). Stay inside it."


# Stretch: the findings-addressed rule from the capstone ladder.


def open_findings(events: list[dict]) -> list[str]:
    """Return the sorted ids of findings that are not closed.

    A finding is closed only by a later fix with the same id, followed by a
    passing (exit 0) verification after that fix.
    """
    still_open: set[str] = set()
    for finding in (event for event in events if event["type"] == "finding"):
        fix_turns = [
            event["turn"]
            for event in events
            if event["type"] == "fix"
            and event.get("id") == finding.get("id")
            and event["turn"] > finding["turn"]
        ]
        verified = bool(fix_turns) and any(
            event["type"] == "verification"
            and event.get("exit") == 0
            and event["turn"] > min(fix_turns)
            for event in events
        )
        if not verified:
            still_open.add(str(finding.get("id")))
    return sorted(still_open)
