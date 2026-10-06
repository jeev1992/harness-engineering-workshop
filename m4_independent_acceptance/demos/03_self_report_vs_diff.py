"""
Demo 03 — Self-report versus the diff
=====================================
A scope check needs the list of paths the work changed. Where does that list
come from? If it comes from the maker's own transcript, the check inherits
every omission the maker makes.

Here the maker adds delete() to kb/kb.py and reports it. It also quietly
rewrites a seed document so its answers look better, and never mentions it.
The same scope rule judges both lists.

Run:
    python m4_independent_acceptance/demos/03_self_report_vs_diff.py

You will see:
    1. The declared scope
    2. The changes the maker reported, and what the rule says about them
    3. The changes git observes, and what the rule says about those

The project is kept under m4_independent_acceptance/demos/runs/self-report/project.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from m1_scope_and_state.rules import scope_violations
from shared.project import changed_paths, create_project, remove_tree
from shared.scenario import BUGGY_DELETE, PLAN_SCOPE

RUN = Path(__file__).resolve().parent / "runs" / "self-report"
SILENT_EDIT = "kb/seed/retrieval-plan.md"


def verdict(label: str, paths: list[str]) -> None:
    violations = scope_violations(PLAN_SCOPE, paths)
    print(f"  {label}: {', '.join(paths)}")
    if violations:
        print(f"  FAIL out of scope: {', '.join(violations)}\n")
    else:
        print("  PASS everything inside the declared scope\n")


def main() -> int:
    remove_tree(RUN)
    project = create_project(RUN / "project", git=True)

    kb_file = project / "kb" / "kb.py"
    kb_file.write_text(
        kb_file.read_text(encoding="utf-8").replace("\n\ndef main(", "\n\n" + BUGGY_DELETE + "\n\ndef main("),
        encoding="utf-8",
        newline="\n",
    )
    seed = project / SILENT_EDIT
    seed.write_text(
        seed.read_text(encoding="utf-8") + "\nDeletion always updates every index automatically.\n",
        encoding="utf-8",
        newline="\n",
    )
    reported = ["kb/kb.py"]

    print(f"1. Declared scope: {', '.join(PLAN_SCOPE)}\n")
    print("2. Scope from the maker's transcript")
    verdict("reported", reported)
    print("3. Scope from git status")
    verdict("observed", changed_paths(project))
    print("Same rule, different input. A check is only as honest as its evidence:")
    print("measure what changed, do not ask the maker what it changed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
