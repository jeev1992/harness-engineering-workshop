"""
Demo 01 — Observe: one unit of evidence
=======================================
Evidence is three things recorded together: the command, its exit code, and
the output it produced. This demo runs one verification command as a separate
process inside a freshly seeded copy of the project and prints exactly that.

Run:
    python m2_executable_verification/demos/01_observe.py                     # kb list
    python m2_executable_verification/demos/01_observe.py --command "kb ask deletion"
    python m2_executable_verification/demos/01_observe.py --command "kb test"

You will see:
    {"command": ..., "process": ..., "exit": ..., "observed": ...}

"process" is the real command line the harness ran. Copy "observed" into
m2_executable_verification/exercises/feature_list.json during the exercise.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from m2_executable_verification.rules import VERIFICATION_COMMANDS, describe, execute
from shared.project import fresh_project


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--command", choices=list(VERIFICATION_COMMANDS), default="kb list")
    command = parser.parse_args().command
    with fresh_project() as project:
        exit_code, observed = execute(command, project)
    print(json.dumps({"command": command, "process": describe(command), "exit": exit_code, "observed": observed}, indent=2))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
