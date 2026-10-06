"""
Demo 03 — The next session
==========================
Work outlives any single session. The next one might be a fresh agent, a
parallel agent, a teammate, or you tomorrow. None of them has the transcript;
all they have is what the repository says.

Session 1 is the baseline maker: it committed a delete() that forgets the
index, marked it passing with evidence it never ran, and left a one-line
handoff. Session 2 is asked to build the next feature, document import.

Run:
    python m3_continuity/demos/03_next_session.py

You will see:
    1. What session 1 left in the repository
    2. Session 2 without a doctor: it trusts the record, builds import, and its
       own import looks broken. The real cause is session 1's delete.
    3. Session 2 with a doctor: it refuses to start on a lie, repairs delete,
       and import works the first time

The sessions are kept under m3_continuity/demos/runs/next-session/.
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from m3_continuity.rules import doctor
from shared.checks import format_checks, load_json
from shared.project import commit, remove_tree, run_kb
from shared.scenario import BUGGY_DELETE, FIXED_DELETE, IMPORT_SOURCE, PLAN_SCOPE, add_before_main, build_run, edit

RUN = Path(__file__).resolve().parent / "runs" / "next-session"
QUESTION = "Where must imported documents appear?"


def session_two(session_one: Path, label: str, with_doctor: bool, inbox: Path) -> None:
    project = RUN / f"session-2-{label}"
    shutil.copytree(session_one, project)
    plan = {
        "work_item": "Implement document import end to end",
        "feature": "import-command",
        "acceptance": "kb import-roundtrip",
        "allowed_paths": PLAN_SCOPE,
    }
    (project / "plan.json").write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    commit(project, "plan: import")

    if with_doctor:
        failing = [check for check in doctor(project, project) if not check.passed]
        print("  starts by running the doctor:")
        print("    " + format_checks(failing).replace("\n", "\n    "))
        print("  not ready: the record says delete works and it does not. Repair first:")
        edit(project, "kb/kb.py", lambda text: text.replace(BUGGY_DELETE, FIXED_DELETE))
        run_kb(project, "reconcile")
        print("    fixed delete() to update the index, reconciled the dangling entry")
    else:
        print("  reads the handoff, sees delete-command 'passing', and starts on import")

    edit(project, "kb/kb.py", add_before_main(IMPORT_SOURCE))
    print("  adds import_document() to kb/kb.py and tries it on the project's data:")
    for args in (("import", str(inbox / "release-notes.md")), ("ask", QUESTION)):
        exit_code, output = run_kb(project, *args)
        print(f"    kb {args[0]:<7} exit {exit_code}  {output}")


def main() -> int:
    remove_tree(RUN)
    session_one = build_run("single-role", RUN) / "project"
    commit(session_one, "session 1: delete (claimed done)")
    inbox = RUN / "inbox"
    inbox.mkdir()
    (inbox / "release-notes.md").write_text(
        "# Release Notes\n\nImported documents must appear in the index immediately.\n", encoding="utf-8"
    )

    print("1. What session 1 left in the repository (committed):")
    print("  session-handoff.md: " + " / ".join(
        line for line in (session_one / "session-handoff.md").read_text(encoding="utf-8").splitlines() if line.startswith("- ")
    ))
    for feature in load_json(session_one / "feature_list.json"):
        print(f"  feature_list.json:  {feature['id']} is {feature['status']}")

    print("\n2. Session 2 WITHOUT a doctor")
    session_two(session_one, "without-doctor", False, inbox)
    print("  -> the new feature looks broken. Session 2 now debugs its own import for a bug in delete.")

    print("\n3. Session 2 WITH a doctor")
    session_two(session_one, "with-doctor", True, inbox)
    print("  -> import works the first time, because the session started from the truth.")
    print("\nThe handoff is for whoever comes next. A doctor makes them check it before trusting it.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
