"""
Scope guard — a Claude Code PreToolUse hook (Module 1, enforced)
================================================================
Module 1 declares scope in plan.json. Written as prose ("only touch kb/"), a
rule like that is often ignored. This hook enforces it before the edit
happens: Claude Code runs it on every Write/Edit, passes the tool call as JSON
on stdin, and blocks the call when this script exits 2. Whatever the script
prints to stderr is what Claude reads as the reason.

    allowed   an edit inside plan.json "allowed_paths"
    allowed   feature_list.json and session-handoff.md (work-tracking state)
    blocked   any other file in the project
    blocked   plan.json itself: the maker may not widen its own scope
    blocked   any edit when no plan exists yet
    ignored   every other tool (Read, Grep, Bash, ...) — exit 0, no opinion

What it cannot see: a shell command such as `echo x > notes.md`. That is why
the done gate checks scope again from `git status` (defense in depth).

Wire it up in .claude/settings.json:
    {"hooks": {"PreToolUse": [{"matcher": "Write|Edit|MultiEdit|NotebookEdit",
      "hooks": [{"type": "command",
                 "command": "python \\"${CLAUDE_PROJECT_DIR}/.harness/scope_guard.py\\""}]}]}}

See it on the wire:
    python m1_scope_and_state/demos/03_scope_guard.py
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from m1_scope_and_state.rules import scope_violations
from shared.project import STATE_FILES

EDIT_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}
ALLOW, BLOCK = 0, 2  # Claude Code blocks a tool call only on exit code 2.


def _relative(file_path: str, project: Path) -> str | None:
    """The path inside the project, with '/' separators; None when it is outside."""
    file = os.path.normcase(os.path.abspath(file_path))
    root = os.path.normcase(os.path.abspath(project))
    try:
        if os.path.commonpath([file, root]) != root:
            return None
    except ValueError:  # different drives on Windows
        return None
    return os.path.relpath(file, root).replace("\\", "/")


def _same(path: str) -> str:
    return os.path.normcase(path.replace("/", os.sep)).replace("\\", "/")


def decide(event: dict, project: Path) -> tuple[int, str]:
    """Return (exit code, message for Claude) for one PreToolUse event, reading plan.json from disk."""
    plan_path = Path(project) / "plan.json"
    plan = json.loads(plan_path.read_text(encoding="utf-8")) if plan_path.is_file() else None
    return judge(event, project, plan)


def judge(event: dict, project: Path | str, plan: dict | None) -> tuple[int, str]:
    """The guard's rules as a pure function: one event, the project root, and the plan (or None)."""
    project = Path(project)
    if event.get("tool_name") not in EDIT_TOOLS:
        return ALLOW, ""
    tool_input = event.get("tool_input") or {}
    file_path = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
    relative = _relative(file_path, project)
    if relative is None:
        return BLOCK, f"Blocked: {file_path} is outside the project. Edit only files inside {project}."
    if relative in {_same(name) for name in STATE_FILES}:
        return ALLOW, ""
    if plan is None:
        return BLOCK, (
            f"Blocked: no plan.json, so no edit is in scope yet ({relative}). "
            'A planner must commit plan.json with "allowed_paths" first.'
        )
    if relative == _same("plan.json"):
        return BLOCK, (
            "Blocked: plan.json belongs to the planner. Do not widen your own scope; "
            "stop and ask for the plan to be changed."
        )
    allowed = plan.get("allowed_paths", [])
    if scope_violations([_same(path) for path in allowed], [relative]):
        return BLOCK, (
            f"Blocked: {relative} is outside the declared scope ({', '.join(allowed) or 'none'}). "
            "Stay inside it, or stop and ask the planner to widen plan.json."
        )
    return ALLOW, ""


def main() -> int:
    event = json.load(sys.stdin)
    project = Path(os.environ.get("CLAUDE_PROJECT_DIR") or event.get("cwd") or Path.cwd())
    code, message = decide(event, project)
    if message:
        print(message, file=sys.stderr)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
