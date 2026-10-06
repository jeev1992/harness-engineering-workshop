"""
Demo 01 — The doctor: can a fresh session trust this repository?
=================================================================
Before a new session selects work, it should check that the repository can
explain itself. The doctor runs three groups of checks over example_repo/:

    router-targets          every link in AGENTS.md resolves
    feature state           known statuses, WIP=1, evidence on passing features
    evidence-reproduces     recorded evidence still reproduces when re-run
    handoff-sections        verified / unverified / next step are all present

Run:
    python m3_continuity/demos/01_doctor.py

Then open m3_continuity/example_repo/ and read it the way a fresh session
would: AGENTS.md first, then the handoff, then the feature list.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from m3_continuity.rules import doctor
from shared.checks import print_checks
from shared.project import fresh_project

EXAMPLE_REPO = Path(__file__).resolve().parents[1] / "example_repo"


def main() -> int:
    with fresh_project() as project:
        healthy = print_checks(doctor(EXAMPLE_REPO, project))
    print("\nReady to select work." if healthy else "\nNot ready: repair the repository before editing.")
    return 0 if healthy else 1


if __name__ == "__main__":
    raise SystemExit(main())
