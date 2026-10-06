"""
Demo 03 — The scope guard, on the wire
======================================
Module 1's declared scope, enforced before an edit happens. This demo runs the
real Claude Code PreToolUse hook (hooks/scope_guard.py) as a separate process,
exactly as Claude Code would: a tool call as JSON on stdin, then the hook's
exit code (0 allow, 2 block) and the stderr text Claude would read.

Run:
    python m1_scope_and_state/demos/03_scope_guard.py

You will see:
    1. One raw PreToolUse event, as Claude Code sends it
    2. Seven tool calls and the hook's verdict on each
    3. The gap: a shell command writes a file the guard never sees, and git
       catches it anyway (why the done gate checks scope again)
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from m1_scope_and_state.rules import scope_violations
from shared.project import changed_paths, commit, create_project, remove_tree

HOOK = Path(__file__).resolve().parents[1] / "hooks" / "scope_guard.py"
RUN = Path(__file__).resolve().parent / "runs" / "scope-guard"
SCOPE = ["kb/kb.py", "kb/test_kb.py"]


def call_hook(event: dict, project: Path) -> tuple[int, str]:
    result = subprocess.run(
        [sys.executable, str(HOOK)],
        input=json.dumps(event),
        capture_output=True,
        text=True,
        env={**os.environ, "CLAUDE_PROJECT_DIR": str(project)},
        check=False,
    )
    return result.returncode, result.stderr.strip()


def edit(tool: str, path: Path, project: Path) -> dict:
    return {
        "session_id": "demo",
        "cwd": str(project),
        "hook_event_name": "PreToolUse",
        "tool_name": tool,
        "tool_input": {"file_path": str(path), "content": "..."},
    }


def main() -> int:
    remove_tree(RUN)
    project = create_project(RUN / "project", git=True)
    (project / "plan.json").write_text(
        json.dumps({"work_item": "Implement document deletion end to end", "allowed_paths": SCOPE}, indent=2) + "\n",
        encoding="utf-8",
    )
    commit(project, "plan: declare scope")

    cases = [
        ("edit the code in scope", edit("Edit", project / "kb" / "kb.py", project)),
        ("add a test in scope", edit("Write", project / "kb" / "test_kb.py", project)),
        ("tune an unrelated file", edit("Write", project / "config" / "retrieval-notes.md", project)),
        ("widen its own scope", edit("Edit", project / "plan.json", project)),
        ("update work-tracking state", edit("Write", project / "feature_list.json", project)),
        ("write outside the project", edit("Write", RUN / "elsewhere.txt", project)),
        ("run a shell command", {
            "session_id": "demo", "cwd": str(project), "hook_event_name": "PreToolUse",
            "tool_name": "Bash", "tool_input": {"command": "echo tweak > notes.md"},
        }),
    ]

    print(f"Declared scope (plan.json): {', '.join(SCOPE)}\n")
    print("1. What Claude Code sends the hook on stdin for one tool call:")
    print("  " + json.dumps(cases[2][1], indent=2).replace("\n", "\n  "))

    print("\n2. The hook's verdict on each tool call:")
    for label, event in cases:
        code, message = call_hook(event, project)
        target = event["tool_input"].get("file_path") or event["tool_input"].get("command")
        shown = os.path.relpath(target, project).replace("\\", "/") if "file_path" in event["tool_input"] else target
        verdict = "exit 0  allowed" if code == 0 else "exit 2  BLOCKED"
        print(f"  {label:<28}{event['tool_name']:<6}{shown:<30}{verdict}")
        if message:
            print(f"  {'':<34}stderr -> Claude: {message}")

    print("\n3. The gap: the guard has no opinion on shell commands. Run that one for real:")
    (project / "notes.md").write_text("tweak\n", encoding="utf-8")
    changed = changed_paths(project)
    print(f"  git status shows: {', '.join(changed)}")
    print(f"  outside scope:    {', '.join(scope_violations(SCOPE, changed)) or 'nothing'}")
    print("\nA guard before the edit plus a check of the real diff after it: neither alone is enough.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
