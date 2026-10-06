"""
Demo 01 — The ladder: same maker, three harnesses
=================================================
The maker from Module 1's baseline runs the same work item three times. It
makes exactly the same mistakes every time. Only the roles around it change:

    single-role     the maker alone; it accepts its own claim
    gen-eval        a checker executes the rubric; the maker repairs findings
    plan-gen-eval   a planner declares scope first, so drift is caught too

Run:
    python m4_independent_acceptance/demos/01_ladder.py

You will see each setup's five rubric results and the scores 0 -> 4 -> 5.
Read the FAIL lines before the scores. Every run is a real git project under
m4_independent_acceptance/demos/runs/<setup>/project/ — open
gen-eval/project/config/retrieval-notes.md to see the out-of-scope edit that
shipped.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from shared.scenario import print_ladder

RUNS = Path(__file__).resolve().parent / "runs"

if __name__ == "__main__":
    raise SystemExit(print_ladder(RUNS))
