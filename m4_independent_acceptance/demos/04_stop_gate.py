"""
Demo 04 — The stop gate, on the wire
====================================
Module 4's rule, enforced: the maker does not get to decide it is done. This
demo runs the real Claude Code Stop hook (hooks/stop_gate.py) as a separate
process, the way Claude Code does when its agent tries to finish, against two
finished runs of the delete work item:

    single-role     the baseline maker, which claims "delete works"
    plan-gen-eval   the same maker after a planner and a checker

Run:
    python m4_independent_acceptance/demos/04_stop_gate.py

You will see, for each run, the Stop event Claude Code sends, the hook's exit
code (2 = "keep working"), and the exact text Claude would read: every failed
control with its fix line. Then try:

    python m4_independent_acceptance/gate.py --explain
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from shared.project import remove_tree
from shared.scenario import build_run

HOOK = Path(__file__).resolve().parents[1] / "hooks" / "stop_gate.py"
RUNS = Path(__file__).resolve().parent / "runs" / "stop-gate"


def stop_event(project: Path) -> dict:
    return {
        "session_id": "demo",
        "cwd": str(project),
        "hook_event_name": "Stop",
        "stop_hook_active": False,
        "last_assistant_message": "Delete works; listing unaffected.",
    }


def main() -> int:
    remove_tree(RUNS)
    for config in ("single-role", "plan-gen-eval"):
        project = build_run(config, RUNS) / "project"
        event = stop_event(project)
        result = subprocess.run(
            [sys.executable, str(HOOK)],
            input=json.dumps(event),
            capture_output=True,
            text=True,
            env={**os.environ, "CLAUDE_PROJECT_DIR": str(project)},
            check=False,
        )
        print(f"== {config}: the agent says \"{event['last_assistant_message']}\" and tries to stop")
        if result.returncode == 2:
            print("exit 2: Claude Code keeps the agent working. Claude reads:\n")
            print("  " + result.stderr.strip().replace("\n", "\n  "))
        else:
            print(f"exit {result.returncode}: every control passes. The agent may finish.")
        print()
    print("Same claim, two outcomes. The gate, not the maker, decides when the work is done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
