"""
Demo 02 — The ladder, scored with your own code
===============================================
Same ladder as Demo 01, but four rubric items are now scored by functions
you wrote in the exercises:

    scope-fidelity       m1 scope_gate.py   scope_violations()   (Module 1 stretch)
    evidence-true        m2 evidence.py     reproduce()
    clean-state          m3 handoff.py      resume_ready()
    findings-addressed   m4 guard.py        open_findings()      (Module 4 stretch)

Anything you have not implemented falls back to the reference, and the
header says so.

Run:
    python m4_independent_acceptance/demos/02_ladder_with_your_code.py

Did you get exactly 0 -> 4 -> 5? If a rung moved, the check behind it
accepts something it should reject, or rejects something it should accept.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from shared.scenario import print_ladder

RUNS = Path(__file__).resolve().parent / "runs"

if __name__ == "__main__":
    raise SystemExit(print_ladder(RUNS, mine=True))
