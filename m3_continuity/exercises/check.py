"""
Check — Module 3, Exercise 1: the handoff parser
================================================
Runs the contract cases against your parse_handoff() and resume_ready() and
checks the session-handoff.md in this folder.

Run:
    python m3_continuity/exercises/check.py              # your work
    python m3_continuity/exercises/check.py --stretch    # optional stretch
    python m3_continuity/exercises/check.py --solution   # the reference solution
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from m3_continuity.rules import validate_handoff
from shared.checks import Check, contract_check, guarded, load_exercise, run_check_cli

EXERCISE_DIR = Path(__file__).resolve().parent
SOLUTION_DIR = EXERCISE_DIR.parent / "solution" / "ex01_handoff_parser"
CODE = "handoff.py"
EDIT = [CODE, "session-handoff.md"]
# A fresh checkout must fail on exactly these checks, and the solution on none.
STARTER_FAILS_WITH = {"continuity-function-contract", "handoff-sections"}


def check_function(base: Path) -> Check:
    module = load_exercise(base / CODE)
    complete = (
        "# Handoff\n\n## Verified now\n\n- Listing passed.\n\n"
        "## Broken or unverified\n\n- Delete pending.\n\n"
        "## Next best step\n\n- Verify delete.\n\n## Notes\n\n- Preserve this section.\n"
    )
    incomplete = "# Handoff\n\n## Verified now\n\n- Listing passed.\n"
    empty_required = (
        "# Handoff\n\n## Verified now\n\n- Listing passed.\n\n"
        "## Broken or unverified\n\n## Next best step\n\n- Verify delete.\n"
    )
    results = [
        module.parse_handoff(complete),
        module.resume_ready(complete),
        module.resume_ready(incomplete),
        module.resume_ready(empty_required),
    ]
    expected = [
        {
            "Verified now": ["Listing passed."],
            "Broken or unverified": ["Delete pending."],
            "Next best step": ["Verify delete."],
            "Notes": ["Preserve this section."],
        },
        {"ready": True, "missing": []},
        {"ready": False, "missing": ["Broken or unverified", "Next best step"]},
        {"ready": False, "missing": ["Broken or unverified"]},
    ]
    return contract_check("continuity-function-contract", results, expected)


def check(base: Path) -> list[Check]:
    return [
        guarded("continuity-function-contract", lambda: check_function(base)),
        *validate_handoff(base / "session-handoff.md"),
    ]


def check_stretch_function(base: Path) -> Check:
    module = load_exercise(base / CODE)
    sections = {
        "Verified now": ["Listing passed."],
        "Broken or unverified": ["Delete pending."],
        "Next best step": ["Verify delete."],
        "Risks": ["Index may be stale."],
        "Notes": [],
    }
    rendered = module.render_handoff("Session handoff", sections)
    reparsed = module.parse_handoff(rendered)
    results = [
        rendered.splitlines()[0],
        reparsed,
        list(reparsed),
        module.resume_ready(rendered),
        rendered.endswith("\n") and not rendered.endswith("\n\n"),
        module.render_handoff("Session handoff", reparsed) == rendered,
    ]
    expected = ["# Session handoff", sections, list(sections), {"ready": True, "missing": []}, True, True]
    return contract_check("stretch:render-handoff", results, expected)


def check_stretch(base: Path) -> list[Check]:
    return [guarded("stretch:render-handoff", lambda: check_stretch_function(base))]


if __name__ == "__main__":
    run_check_cli(
        exercise_dir=EXERCISE_DIR,
        solution_dir=SOLUTION_DIR,
        edit=EDIT,
        check=check,
        check_stretch=check_stretch,
    )
