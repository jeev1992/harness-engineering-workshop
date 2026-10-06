"""The scripted agent, the delete work item, and the five-check rubric.

One scripted maker performs the same work item under three role setups. Each
run gets its own git copy of the kb project under runs/<setup>/project/. The
maker's edits are real edits to that copy's code, its commands run that
code as separate processes, and scope is read from git, not from the maker's
own account. The opening demo (Module 1) and the capstone ladder (Module 4)
both run on this file. You never need to edit it.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

from m1_scope_and_state.exercises import check as m1_check
from m1_scope_and_state.rules import scope_violations
from m2_executable_verification.exercises import check as m2_check
from m2_executable_verification.rules import execute, reproduce
from m3_continuity.exercises import check as m3_check
from m3_continuity.rules import resume_ready
from m4_independent_acceptance.exercises import check as m4_check
from m4_independent_acceptance.rules import open_findings
from shared.checks import ROOT, Check, guarded, load_exercise, load_json
from shared.project import changed_paths, commit, create_project, fresh_project, remove_tree, run_kb

WORK_ITEM = "Implement document deletion end to end"
PLAN_SCOPE = ["kb/kb.py", "kb/test_kb.py"]
CONFIGS = ("single-role", "gen-eval", "plan-gen-eval")
RUBRIC = (
    "verification-before-done",
    "evidence-true",
    "findings-addressed",
    "scope-fidelity",
    "clean-state",
)

# What the maker writes. The first version forgets the derived index.
BUGGY_DELETE = '''def delete(data_dir: Path, document_id: str) -> dict[str, object]:
    """Delete a document."""
    entries = _read_index(data_dir)
    match = next((entry for entry in entries if entry["id"] == document_id), None)
    if match is None:
        raise ValueError(f"unknown document: {document_id}")
    (data_dir / "documents" / str(match["filename"])).unlink()
    return {"deleted": document_id}
'''
FIXED_DELETE = '''def delete(data_dir: Path, document_id: str) -> dict[str, object]:
    """Delete a document's source file and its index entry."""
    entries = _read_index(data_dir)
    match = next((entry for entry in entries if entry["id"] == document_id), None)
    if match is None:
        raise ValueError(f"unknown document: {document_id}")
    (data_dir / "documents" / str(match["filename"])).unlink()
    _write_index(data_dir, [entry for entry in entries if entry["id"] != document_id])
    return {"deleted": document_id, "remaining": len(entries) - 1}
'''
DELETE_TEST = '''

class DeleteTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.data_dir = Path(self.temporary.name)
        kb.init(self.data_dir, ROOT / "kb" / "seed")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_delete_updates_source_and_index(self) -> None:
        report = kb.delete(self.data_dir, "team-meeting")
        self.assertEqual(report, {"deleted": "team-meeting", "remaining": 2})
        self.assertFalse((self.data_dir / "documents" / "team-meeting.txt").exists())
        ids = [item["id"] for item in kb.list_documents(self.data_dir)["documents"]]
        self.assertNotIn("team-meeting", ids)
        self.assertTrue(kb.ask(self.data_dir, "How must deletion update state?")["citations"])
'''
ROGUE_EDIT = "config/retrieval-notes.md"
# The second feature: what a later session builds once delete is done.
IMPORT_SOURCE = '''def import_document(data_dir: Path, source: Path) -> dict[str, object]:
    """Copy a document into the knowledge base and index it."""
    if not source.is_file():
        raise ValueError(f"no such file: {source}")
    target = data_dir / "documents" / source.name
    if target.exists():
        raise ValueError(f"document already exists: {source.stem}")
    shutil.copy2(source, target)
    entries = [entry for entry in _read_index(data_dir) if entry["id"] != source.stem]
    _write_index(data_dir, [*entries, _metadata(target)])
    return {"imported": source.stem, "documents": len(entries) + 1}
'''


# ------------------------------------------------------------ the scripted run


class _Transcript:
    def __init__(self) -> None:
        self.events: list[dict] = []

    def add(self, role: str, kind: str, **detail: object) -> None:
        self.events.append({"turn": len(self.events) + 1, "role": role, "type": kind, **detail})


def edit(project: Path, relative: str, change: Callable[[str], str]) -> None:
    path = project / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    before = path.read_text(encoding="utf-8") if path.exists() else ""
    after = change(before)
    if after == before:
        raise RuntimeError(f"scripted edit changed nothing in {relative}")
    path.write_text(after, encoding="utf-8", newline="\n")


def add_before_main(source: str) -> Callable[[str], str]:
    anchor = "\n\ndef main("
    def change(text: str) -> str:
        if text.count(anchor) != 1:
            raise RuntimeError("kb/kb.py no longer has exactly one main(); update the scripted maker")
        return text.replace(anchor, "\n\n" + source + anchor)
    return change


def build_run(config: str, root: Path) -> Path:
    run = root / config
    run.mkdir(parents=True)
    project = create_project(run / "project", git=True)
    transcript = _Transcript()

    def verify(command: str) -> None:
        exit_code, observed = execute(command, project)
        transcript.add("checker", "verification", command=command, exit=exit_code, observed=observed)

    if config == "plan-gen-eval":
        # The planner commits the plan, so any later change to it shows up in git as a violation.
        plan = {
            "work_item": WORK_ITEM,
            "feature": "delete-command",
            "acceptance": "kb delete-roundtrip",
            "allowed_paths": PLAN_SCOPE,
        }
        (project / "plan.json").write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
        commit(project, "plan: declare scope")
        transcript.add("planner", "plan", detail=f"allowed scope: {', '.join(PLAN_SCOPE)}")

    # The maker behaves identically in every configuration.
    edit(project, "kb/kb.py", add_before_main(BUGGY_DELETE))
    transcript.add("maker", "edit", target="kb/kb.py", detail="added delete(): removes the source file")
    run_kb(project, "delete", "team-meeting")
    transcript.add("maker", "action", command="kb delete team-meeting", detail="ran the new delete")
    edit(project, ROGUE_EDIT, lambda _: "# Retrieval notes\n\n- Prefer longer tokens.\n")
    transcript.add("maker", "edit", target=ROGUE_EDIT, detail="tuned retrieval notes while in the area")
    features = [
        {
            "id": "delete-command",
            "status": "passing",
            "evidence": {"command": "kb ask deletion", "observed": "exit 0: assumed"},
        },
        {"id": "surviving-list", "status": "passing", "evidence": {}},
    ]
    transcript.add("maker", "claim", detail="delete works; listing unaffected")

    if config == "single-role":
        transcript.add("maker", "done", detail="the maker accepts its own claim")
        handoff = "# Session handoff\n\n## Verified now\n\n- Delete implemented and working.\n"
    else:
        verify("kb ask deletion")
        transcript.add(
            "checker", "finding", id="derived-state", target="data/index/documents.json",
            detail="index still lists team-meeting after its file was deleted",
        )
        transcript.add(
            "checker", "finding", id="evidence:delete-command",
            detail="recorded observation was never produced by execution",
        )
        transcript.add(
            "checker", "finding", id="evidence:surviving-list", detail="passing without evidence"
        )
        # The checker reads what changed from git, not from the maker's transcript.
        drift = scope_violations(PLAN_SCOPE, changed_paths(project)) if config == "plan-gen-eval" else []
        for path in drift:
            transcript.add(
                "checker", "finding", id=f"out-of-scope:{path}", target=path,
                detail="git shows a change outside the declared scope",
            )

        edit(project, "kb/kb.py", lambda text: text.replace(BUGGY_DELETE, FIXED_DELETE))
        edit(project, "kb/test_kb.py", lambda text: text + DELETE_TEST)
        run_kb(project, "reconcile")
        transcript.add(
            "maker", "fix", id="derived-state", target="kb/kb.py",
            detail="delete() now removes the index entry; added a test; reconciled the dangling entry",
        )
        for feature, command in zip(features, ("kb ask deletion", "kb list"), strict=True):
            _, observed = execute(command, project)
            feature["evidence"] = {"command": command, "observed": observed}
            transcript.add(
                "maker", "fix", id=f"evidence:{feature['id']}", detail="recorded a real observation"
            )
        for path in drift:
            (project / path).unlink()
            transcript.add(
                "maker", "fix", id=f"out-of-scope:{path}", detail="reverted the out-of-scope edit"
            )
        verify("kb test")
        verify("kb ask deletion")
        verify("kb list")
        transcript.add("checker", "done", detail="the checker accepts after re-verification")
        handoff = (
            "# Session handoff\n\n## Verified now\n\n"
            "- kb test, kb ask deletion, and kb list pass against the reconciled index.\n\n"
            "## Broken or unverified\n\n- kb/test_kb.py does not yet cover reconciling a dangling index entry.\n\n"
            "## Next best step\n\n- Add a test that reconcile drops an index entry whose file is gone.\n"
        )

    # The transcript is the session's record; the work-tracking state lives in the repository.
    (run / "transcript.json").write_text(json.dumps(transcript.events, indent=2) + "\n", encoding="utf-8")
    (project / "feature_list.json").write_text(json.dumps(features, indent=2) + "\n", encoding="utf-8")
    (project / "session-handoff.md").write_text(handoff, encoding="utf-8")
    return run


# ------------------------------------------------------------------ the rubric


@dataclass(frozen=True)
class Predicates:
    """The rubric's swappable parts. Your exercise code can stand in for each."""

    reproduce: Callable[[dict, Callable[[str], tuple[int, str]]], dict] = reproduce
    open_findings: Callable[[list[dict]], list[str]] = open_findings
    scope_violations: Callable[[list[str], list[str]], list[str]] = scope_violations
    resume_ready: Callable[[str], dict] = resume_ready


def score_run(run: Path, predicates: Predicates | None = None) -> list[Check]:
    predicates = predicates or Predicates()
    project = run / "project"
    events = load_json(run / "transcript.json")
    features = load_json(project / "feature_list.json")
    passing = [feature for feature in features if feature.get("status") == "passing"]

    def runner(command: str) -> tuple[int, str]:
        return execute(command, project)

    def verification_before_done() -> Check:
        done_turn = max((event["turn"] for event in events if event["type"] == "done"), default=-1)
        verified = {
            event.get("command")
            for event in events
            if event["type"] == "verification" and event.get("exit") == 0 and event["turn"] < done_turn
        }
        missing = [
            feature.get("evidence", {}).get("command") or f"{feature['id']} (no command)"
            for feature in passing
            if feature.get("evidence", {}).get("command") not in verified
        ]
        if missing:
            return Check(RUBRIC[0], False, f"not verified before done: {', '.join(missing)}")
        return Check(RUBRIC[0], True, f"verified before done: {', '.join(sorted(verified))}")

    def evidence_true() -> Check:
        problems = []
        for feature in passing:
            if not feature.get("evidence", {}).get("command"):
                problems.append(f"{feature['id']} has no evidence")
                continue
            report = predicates.reproduce(feature, runner)
            if not report.get("passed"):
                problems.append(f"{feature['id']} does not reproduce (exit {report.get('exit')})")
        if problems:
            return Check(RUBRIC[1], False, "; ".join(problems))
        return Check(RUBRIC[1], True, f"{len(passing)} evidence records reproduce")

    def findings_addressed() -> Check:
        if not any(event["role"] == "checker" for event in events):
            return Check(RUBRIC[2], False, "no checker ran")
        still_open = predicates.open_findings(events)
        if still_open:
            return Check(RUBRIC[2], False, f"open findings: {', '.join(still_open)}")
        count = sum(event["type"] == "finding" for event in events)
        return Check(RUBRIC[2], True, f"{count} findings closed by fix and re-verification")

    def scope_fidelity() -> Check:
        # Scope is measured from git in the run's project, never from the transcript.
        changed = changed_paths(project)
        plan_path = project / "plan.json"
        if not plan_path.exists():
            return Check(RUBRIC[3], False, f"no plan declared scope; git shows: {', '.join(changed) or 'no changes'}")
        violations = predicates.scope_violations(load_json(plan_path)["allowed_paths"], changed)
        if violations:
            return Check(RUBRIC[3], False, f"git shows out-of-scope changes: {', '.join(violations)}")
        still_open = set(predicates.open_findings(events))
        reverted = sorted(
            str(event.get("target"))
            for event in events
            if event["type"] == "finding"
            and str(event.get("id", "")).startswith("out-of-scope:")
            and event.get("id") not in still_open
        )
        if reverted:
            return Check(RUBRIC[3], True, f"flagged and reverted: {', '.join(reverted)}")
        return Check(RUBRIC[3], True, "every git change is inside the declared scope")

    def clean_state() -> Check:
        report = predicates.resume_ready((project / "session-handoff.md").read_text(encoding="utf-8"))
        if not report.get("ready"):
            missing = ", ".join(report.get("missing", [])) or "unknown"
            return Check(RUBRIC[4], False, f"handoff missing or empty: {missing}")
        return Check(RUBRIC[4], True, "handoff ready for the next session")

    items = (verification_before_done, evidence_true, findings_addressed, scope_fidelity, clean_state)
    return [guarded(name, item) for name, item in zip(RUBRIC, items, strict=True)]


# ------------------------------------------------- scoring with your own code

EXERCISE_DIRS = {
    1: ROOT / "m1_scope_and_state" / "exercises",
    2: ROOT / "m2_executable_verification" / "exercises",
    3: ROOT / "m3_continuity" / "exercises",
    4: ROOT / "m4_independent_acceptance" / "exercises",
}


def _with_fresh_project(check: Callable[[Path, Path], Check]) -> Callable[[Path], Check]:
    def run(base: Path) -> Check:
        with fresh_project() as project:
            return check(base, project)

    return run


# (function name, module, exercise file, rubric item it powers, probe call, contract check)
YOUR_PREDICATES: tuple[tuple[str, int, str, str, Callable[[Callable], object], Callable[[Path], Check]], ...] = (
    ("scope_violations", 1, m1_check.CODE, "scope-fidelity", lambda fn: fn([], []),
     m1_check.check_stretch_function),
    ("reproduce", 2, m2_check.CODE, "evidence-true", lambda fn: fn({"evidence": {}}, lambda _: (2, "")),
     _with_fresh_project(m2_check.check_function)),
    ("resume_ready", 3, m3_check.CODE, "clean-state", lambda fn: fn(""),
     m3_check.check_function),
    ("open_findings", 4, m4_check.CODE, "findings-addressed", lambda fn: fn([]),
     m4_check.check_stretch_function),
)


def load_predicates(exercise_dirs: dict[int, Path]) -> tuple[Predicates, dict[str, str]]:
    """Use each module's exercise code where it is implemented; fall back to the reference."""
    chosen: dict[str, Callable] = {}
    sources: dict[str, str] = {}
    for name, module, code, rubric_item, probe, contract in YOUR_PREDICATES:
        path = exercise_dirs.get(module, Path("/nonexistent")) / code
        label = f"m{module} {code} {name}"
        if not path.is_file():
            sources[rubric_item] = f"reference ({label}: file missing)"
            continue
        try:
            function = getattr(load_exercise(path), name)
            probe(function)
        except NotImplementedError:
            sources[rubric_item] = f"reference ({label}: not implemented)"
            continue
        except AttributeError:
            sources[rubric_item] = f"reference ({label}: function missing)"
            continue
        except Exception:
            pass  # use it anyway; scoring reports the error against the rubric item
        chosen[name] = function
        own_check = guarded(name, lambda base=path.parent, contract=contract: contract(base))
        status = "its check passes" if own_check.passed else f"its check FAILS: {own_check.detail}"
        sources[rubric_item] = f"yours ({label}; {status})"
    return Predicates(**chosen), sources


def build_runs(root: Path) -> dict[str, Path]:
    """Build every setup's run. They are independent, so they run in parallel."""
    with ThreadPoolExecutor(max_workers=len(CONFIGS)) as pool:
        return dict(zip(CONFIGS, pool.map(lambda config: build_run(config, root), CONFIGS), strict=True))


def print_ladder(runs: Path, mine: bool = False) -> int:
    """Run all three setups, print every rubric result, and return a process exit code."""
    remove_tree(runs)
    predicates = None
    sources: dict[str, str] = {}
    if mine:
        predicates, sources = load_predicates(EXERCISE_DIRS)
        print("Rubric checks:")
        for item in RUBRIC:
            print(f"  {item:<26}{sources.get(item, 'reference (shared/scenario.py)')}")
        print()
    print("Same maker, same work item, three harnesses.")
    print(f"Each run is kept for inspection under {runs.relative_to(ROOT).as_posix()}/<config>/\n")
    built = build_runs(runs)
    with ThreadPoolExecutor(max_workers=len(CONFIGS)) as pool:
        results = list(pool.map(lambda config: score_run(built[config], predicates), CONFIGS))
    scores = []
    for config, checks in zip(CONFIGS, results, strict=True):
        score = sum(item.passed for item in checks)
        scores.append(score)
        print(f"{config}  {score}/5")
        for item in checks:
            print(f"  {'PASS' if item.passed else 'FAIL'} {item.name:<26}{item.detail}")
        print()
    print("Scores: " + " -> ".join(str(score) for score in scores))
    if mine and any("FAILS" in source for source in sources.values()):
        print("\nA check that fails its own exercise check can still reproduce the ladder: a")
        print("rubric only catches what the run exercises. Fix it before trusting it.")
    if scores == [0, 4, 5]:
        return 0
    print("The reference rubric produces 0 -> 4 -> 5. Find the rung that moved and the")
    print("check behind it: that check accepts something it should reject, or")
    print("rejects something it should accept.")
    return 1
