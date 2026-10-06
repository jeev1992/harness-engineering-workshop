"""
Instructor: verify the whole workshop from a clean checkout
===========================================================
Run before class. Exits zero only when:

    1. the m3 example repository passes the doctor
    2. the unit tests pass (kb/test_kb.py and instructor/tests/, including
       two-sided tests for the Claude Code hooks)
    3. every exercise starter fails on exactly its recorded checks,
       every solution passes, and every stretch is unimplemented in the
       starter and passing in the solution
    4. lint passes

Run:
    python instructor/verify_all.py

Step 3 checks the files in each module's exercises/ folder, so run this on
a clean checkout, not on a copy where exercises have been solved.
"""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from m1_scope_and_state.exercises import check as m1_check
from m2_executable_verification.exercises import check as m2_check
from m3_continuity.exercises import check as m3_check
from m3_continuity.rules import doctor
from m4_independent_acceptance.exercises import check as m4_check
from shared.checks import print_checks
from shared.project import fresh_project

MODULE_CHECKS = {1: m1_check, 2: m2_check, 3: m3_check, 4: m4_check}


def section(title: str) -> None:
    print(f"\n== {title}", flush=True)


def verify_exercises() -> bool:
    ok = True
    for module, check in MODULE_CHECKS.items():
        failures = {item.name for item in check.check(check.EXERCISE_DIR) if not item.passed}
        starter_ok = failures == check.STARTER_FAILS_WITH
        solution_ok = all(item.passed for item in check.check(check.SOLUTION_DIR))
        stretch_ok = not any(item.passed for item in check.check_stretch(check.EXERCISE_DIR)) and all(
            item.passed for item in check.check_stretch(check.SOLUTION_DIR)
        )
        print(f"{'PASS' if starter_ok else 'FAIL'} m{module} starter fails on: {', '.join(sorted(failures)) or 'nothing'}")
        print(f"{'PASS' if solution_ok else 'FAIL'} m{module} solution passes")
        print(f"{'PASS' if stretch_ok else 'FAIL'} m{module} stretch: starter unimplemented, solution passes")
        ok = ok and starter_ok and solution_ok and stretch_ok
    return ok


def main() -> int:
    section("doctor: m3_continuity/example_repo")
    with fresh_project() as project:
        doctor_ok = print_checks(doctor(ROOT / "m3_continuity" / "example_repo", project))

    section("unit tests")
    suite = unittest.defaultTestLoader.loadTestsFromNames(
        ["kb.test_kb", "instructor.tests.test_workshop", "instructor.tests.test_hooks", "instructor.tests.test_live"]
    )
    tests_ok = unittest.TextTestRunner(stream=sys.stdout, verbosity=1).run(suite).wasSuccessful()

    section("exercises")
    exercises_ok = verify_exercises()

    section("lint")
    sys.stdout.flush()
    lint_ok = subprocess.run([sys.executable, str(ROOT / "instructor" / "lint.py")], check=False).returncode == 0

    ok = doctor_ok and tests_ok and exercises_ok and lint_ok
    print(f"\nstatus: {'OK' if ok else 'FAILED'}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
