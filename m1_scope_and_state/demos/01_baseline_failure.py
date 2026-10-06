"""
Demo 01 — The baseline failure
==============================
An agent (the "maker") is asked to add document deletion. It writes a
delete() that removes the file but forgets the index, records evidence it
never ran, edits an unrelated file, and declares itself done. Nothing around
it checks.

The maker is scripted so the class is repeatable, but its work is real: it
edits the code in its own git copy of the project, and every command below
runs that code as a separate process.

Run:
    python m1_scope_and_state/demos/01_baseline_failure.py

You will see:
    1. What the maker did        (its transcript)
    2. What the maker wrote      (the delete() it added to kb/kb.py)
    3. What the maker recorded   (its feature_list.json)
    4. What is actually true     (commands re-run now, and what git says changed)
    5. The rubric: 0 of 5 — the completion claim is not accepted

The run is kept under m1_scope_and_state/demos/runs/single-role/. Open
project/kb/kb.py, project/data/index/documents.json, and transcript.json, or
run `git -C m1_scope_and_state/demos/runs/single-role/project diff`.
The non-zero exit is intentional.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from m2_executable_verification.rules import execute
from shared.checks import ROOT, load_json
from shared.project import changed_paths, remove_tree
from shared.scenario import BUGGY_DELETE, WORK_ITEM, build_run, score_run

RUNS = Path(__file__).resolve().parent / "runs"


def summarize(command: str, exit_code: int, observed: str) -> str:
    if exit_code != 0:
        return observed
    value = json.loads(observed)
    if command == "kb list":
        ids = [document["id"] for document in value["documents"]]
        return f"{len(ids)} indexed: {', '.join(ids)}"
    return f"{len(value['citations'])} citations"


def main() -> int:
    remove_tree(RUNS / "single-role")
    run = build_run("single-role", RUNS)
    project = run / "project"
    shown = run.relative_to(ROOT).as_posix()

    print(f"Work item: {WORK_ITEM}.\n")
    print(f"1. What the maker did ({shown}/transcript.json):")
    for event in load_json(run / "transcript.json"):
        subject = event.get("target") or event.get("command") or ""
        print(f"  {event['turn']:>2} {event['role']:<6} {event['type']:<7} {subject:<28}{event.get('detail', '')}")

    print(f"\n2. What the maker wrote ({shown}/project/kb/kb.py):")
    for line in BUGGY_DELETE.rstrip("\n").splitlines():
        print(f"  | {line}")

    print(f"\n3. What the maker recorded ({shown}/project/feature_list.json):")
    for feature in load_json(project / "feature_list.json"):
        evidence = feature.get("evidence", {})
        record = f"{evidence['command']} -> {evidence['observed']}" if evidence else "(no evidence)"
        print(f"  {feature['id']:<16}{feature['status']:<9}{record}")

    print(f"\n4. What is actually true now (re-executed in {shown}/project):")
    files = sorted(path.name for path in (project / "data" / "documents").iterdir())
    print(f"  {'documents/':<17}{len(files)} files: {', '.join(files)}")
    for command in ("kb list", "kb ask deletion"):
        exit_code, observed = execute(command, project)
        print(f"  {command:<17}exit {exit_code}  {summarize(command, exit_code, observed)}")
    print(f"  {'git status':<17}changed: {', '.join(changed_paths(project))}")

    print("\n5. Rubric:")
    checks = score_run(run)
    for item in checks:
        print(f"  {'PASS' if item.passed else 'FAIL'} {item.name:<26}{item.detail}")
    print(f"\nScore {sum(item.passed for item in checks)} of 5. The completion claim is not accepted.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
