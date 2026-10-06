"""
Check — Module 2, Exercise 1: reproduce recorded evidence
=========================================================
Runs the contract cases against your reproduce() with a real executor and
re-executes the evidence recorded in feature_list.json in this folder.

Run:
    python m2_executable_verification/exercises/check.py              # your work
    python m2_executable_verification/exercises/check.py --stretch    # optional stretch
    python m2_executable_verification/exercises/check.py --solution   # the reference solution
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from m2_executable_verification.rules import execute, validate_evidence
from shared.checks import ROOT, Check, contract_check, guarded, load_exercise, run_check_cli
from shared.project import fresh_project

EXERCISE_DIR = Path(__file__).resolve().parent
SOLUTION_DIR = EXERCISE_DIR.parent / "solution" / "ex01_reproduce_evidence"
CODE = "evidence.py"
EDIT = [CODE, "feature_list.json"]
# A fresh checkout must fail on exactly these checks, and the solution on none.
STARTER_FAILS_WITH = {"evidence-function-contract", "evidence-reproduces:document-list"}


def check_function(base: Path, project: Path) -> Check:
    module = load_exercise(base / CODE)
    _, actual = execute("kb list", project)
    features = [
        {"evidence": {"command": "kb list", "observed": actual}},
        {"evidence": {"command": "kb list", "observed": "exit 0: assumed"}},
        {"evidence": {"command": "unsupported", "observed": ""}},
    ]
    results = [
        module.reproduce(feature, lambda command: execute(command, project)) for feature in features
    ]
    expected = [
        {"passed": True, "exit": 0, "observed": actual},
        {"passed": False, "exit": 0, "observed": actual},
        {
            "passed": False,
            "exit": 2,
            "observed": "unsupported verification command: unsupported",
        },
    ]
    return contract_check("evidence-function-contract", results, expected)


def check(base: Path) -> list[Check]:
    with fresh_project() as project:
        return [
            guarded("evidence-function-contract", lambda: check_function(base, project)),
            *validate_evidence(base / "feature_list.json", project),
        ]


LINT_CASES = {
    # A delete that forgets the index: the baseline maker's code.
    "forgets the index": (
        "def delete(data_dir, document_id):\n"
        "    entries = _read_index(data_dir)\n"
        "    (data_dir / 'documents' / 'x.md').unlink()\n"
        "    return {'deleted': document_id}\n"
    ),
    "updates the index": (
        "def delete(data_dir, document_id):\n"
        "    entries = _read_index(data_dir)\n"
        "    (data_dir / 'documents' / 'x.md').unlink()\n"
        "    _write_index(data_dir, [])\n"
        "    return {'deleted': document_id}\n"
    ),
    "never deletes": "def reconcile(data_dir):\n    _write_index(data_dir, _read_index(data_dir))\n",
    "two offenders": "def purge(p):\n    p.unlink()\n\n\ndef archive(p):\n    p.unlink()\n",
}


def check_stretch_function(base: Path) -> Check:
    lint = load_exercise(base / CODE).lint_derived_state
    reports = {label: lint(source) for label, source in LINT_CASES.items()}
    reports["the real kb/kb.py"] = lint((ROOT / "kb" / "kb.py").read_text(encoding="utf-8"))
    results = [[message.split("()", 1)[0] for message in messages] for messages in reports.values()]
    results.append(all("_write_index" in message for messages in reports.values() for message in messages))
    expected = [["delete"], [], [], ["archive", "purge"], [], True]
    return contract_check("stretch:lint-derived-state", results, expected)


def check_stretch(base: Path) -> list[Check]:
    return [guarded("stretch:lint-derived-state", lambda: check_stretch_function(base))]


if __name__ == "__main__":
    run_check_cli(
        exercise_dir=EXERCISE_DIR,
        solution_dir=SOLUTION_DIR,
        edit=EDIT,
        check=check,
        check_stretch=check_stretch,
    )
