"""
Demo 02 — Fabricated evidence versus re-execution
=================================================
A feature list can say "passing" with an observation attached and still be
false. The only way to know is to run the recorded command again and compare
what it produces now with what was recorded.

Run:
    python m2_executable_verification/demos/02_fabricated_evidence.py

You will see three records judged two ways:
    trusting   — "there is a non-empty observation" (the exercise starter)
    executing  — re-run the command; pass only on exit 0 and an exact match
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from m2_executable_verification.rules import execute, reproduce
from shared.project import fresh_project


def main() -> None:
    with fresh_project() as project:
        _, real = execute("kb list", project)
        records = {
            "real observation": {"command": "kb list", "observed": real},
            "assumed observation": {"command": "kb list", "observed": "exit 0: assumed"},
            "unsupported command": {"command": "kb delete everything", "observed": "ok"},
        }
        print(f"{'record':<22}{'trusting':<11}{'executing':<11}actual exit")
        for label, evidence in records.items():
            trusting = bool(evidence["observed"])
            report = reproduce({"evidence": evidence}, lambda command: execute(command, project))
            print(f"{label:<22}{str(trusting):<11}{str(report['passed']):<11}{report['exit']}")
    print("\nTrusting accepts all three. Only re-execution separates the real record")
    print("from a claim that was never observed, and keeps unknown commands failing.")


if __name__ == "__main__":
    main()
