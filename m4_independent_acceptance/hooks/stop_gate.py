"""
Stop gate — a Claude Code Stop hook (Module 4, enforced)
========================================================
Module 4's rule is that the maker does not accept its own work. This hook
makes that mechanical: when Claude Code's agent tries to finish, Claude Code
runs this script, which runs the done gate (gate.py). If any control fails, the
script exits 2 and Claude Code keeps the agent working, with the failures and
their fix lines (written to stderr) as the reason. "Done" stops being the
maker's call.

Claude Code caps forced continuations at eight in a row, so a control the
agent cannot satisfy ends the session instead of looping forever. The event's
stop_hook_active flag is true while the agent is continuing because of a Stop
hook; this gate does not need it, because every failure here is fixable.

Wire it up in .claude/settings.json:
    {"hooks": {"Stop": [{"hooks": [{"type": "command",
      "command": "python \\"${CLAUDE_PROJECT_DIR}/.harness/stop_gate.py\\""}]}]}}

See it on the wire:
    python m4_independent_acceptance/demos/04_stop_gate.py
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from m4_independent_acceptance.gate import gate
from shared.checks import format_checks

ALLOW, BLOCK = 0, 2  # Claude Code keeps the agent working only on exit code 2.


def decide(event: dict, project: Path) -> tuple[int, str]:
    """Return (exit code, message for Claude) for one Stop event."""
    failing = [check for check in gate(project) if not check.passed]
    if not failing:
        return ALLOW, ""
    return BLOCK, (
        "You are not done: the done gate failed. Fix each item below, then finish again.\n"
        + format_checks(failing)
    )


def main() -> int:
    event = json.load(sys.stdin)
    project = Path(os.environ.get("CLAUDE_PROJECT_DIR") or event.get("cwd") or Path.cwd())
    code, message = decide(event, project)
    if message:
        print(message, file=sys.stderr)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
