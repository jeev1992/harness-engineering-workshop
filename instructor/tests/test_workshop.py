import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from kb import kb
from m1_scope_and_state.exercises import check as m1_check
from m2_executable_verification.exercises import check as m2_check
from m2_executable_verification.rules import execute
from m3_continuity.exercises import check as m3_check
from m3_continuity.rules import doctor, validate_handoff
from m4_independent_acceptance.exercises import check as m4_check
from m4_independent_acceptance.rules import open_findings
from shared.checks import contract_check, load_exercise, load_json
from shared.project import changed_paths, fresh_project, run_kb
from shared.scenario import BUGGY_DELETE, FIXED_DELETE, CONFIGS, EXERCISE_DIRS, build_run, build_runs, load_predicates, score_run

INSTRUCTOR = ROOT / "instructor"
CLOCK = re.compile(r"Clock (\d\d):(\d\d) \| (\d+) min")
MODULE_CHECKS = {1: m1_check, 2: m2_check, 3: m3_check, 4: m4_check}


def core_slides() -> list[str]:
    text = (INSTRUCTOR / "slides.md").read_text(encoding="utf-8")
    body = text.split("\n---\n", 1)[1]
    slides = re.split(r"\n---\n", body)
    core = []
    for slide in slides:
        if re.search(r"^# Appendix$", slide, flags=re.MULTILINE):
            break
        core.append(slide)
    return core


class WorkshopTests(unittest.TestCase):
    runs: dict[str, Path]

    @classmethod
    def setUpClass(cls) -> None:
        # Building a run starts real processes and git; build the three once and share them.
        # Tests that modify a run build their own.
        cls._temp = tempfile.TemporaryDirectory()
        cls.runs = build_runs(Path(cls._temp.name))

    @classmethod
    def tearDownClass(cls) -> None:
        cls._temp.cleanup()

    def test_class_plan_totals_four_hours(self) -> None:
        text = (INSTRUCTOR / "class-plan.md").read_text(encoding="utf-8")
        minutes = [
            int(match.group(1))
            for line in text.splitlines()
            if (match := re.match(r"\| \d\d:\d\d \| (\d+) \|", line))
        ]
        self.assertEqual(sum(minutes), 240)

    def test_core_deck_follows_the_agenda_clock(self) -> None:
        slides = core_slides()
        elapsed = 0
        clocks = set()
        for slide in slides:
            match = CLOCK.search(slide)
            heading = re.search(r"^# (.+)$", slide, flags=re.MULTILINE)
            self.assertIsNotNone(match, f"core slide has no clock: {heading}")
            hours, minutes, duration = (int(group) for group in match.groups())
            self.assertEqual(hours * 60 + minutes, elapsed, f"clock drift at {heading.group(1)}")
            clocks.add(f"{hours:02d}:{minutes:02d}")
            elapsed += duration
        self.assertEqual(elapsed, 240)
        plan = (INSTRUCTOR / "class-plan.md").read_text(encoding="utf-8")
        agenda_starts = set(re.findall(r"^\| (\d\d:\d\d) \|", plan, flags=re.MULTILINE))
        self.assertLessEqual(agenda_starts, clocks, "an agenda segment has no slide")

    def test_example_repo_passes_doctor(self) -> None:
        with fresh_project() as project:
            checks = doctor(ROOT / "m3_continuity" / "example_repo", project)
        self.assertTrue(all(check.passed for check in checks), checks)
        self.assertIn("evidence-reproduces:document-listing", {check.name for check in checks})

    def test_doctor_rejects_empty_required_handoff_section(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "session-handoff.md"
            path.write_text(
                "# H\n\n## Verified now\n\n- x\n\n## Broken or unverified\n\n- y\n\n"
                "## Next best step\n",
                encoding="utf-8",
            )
            self.assertFalse(validate_handoff(path)[0].passed)

    def test_every_starter_fails_and_solution_passes(self) -> None:
        for module, check in MODULE_CHECKS.items():
            starter = check.check(check.EXERCISE_DIR)
            solution = check.check(check.SOLUTION_DIR)
            self.assertEqual(
                {item.name for item in starter if not item.passed},
                check.STARTER_FAILS_WITH,
                f"module {module} starter failed for the wrong reason",
            )
            self.assertTrue(all(item.passed for item in solution), f"module {module} solution failed")

    def test_ladder_scores_are_executable_counts(self) -> None:
        scores = [sum(check.passed for check in score_run(self.runs[config])) for config in CONFIGS]
        self.assertEqual(scores, [0, 4, 5])

    def test_baseline_failure_is_real_state(self) -> None:
        project = self.runs["single-role"] / "project"
        self.assertFalse((project / "data" / "documents" / "team-meeting.txt").exists())
        exit_code, observed = execute("kb ask deletion", project)
        self.assertEqual(exit_code, 1)
        self.assertIn("team-meeting has no source file", observed)
        self.assertTrue((project / "config" / "retrieval-notes.md").exists())

    def test_repaired_runs_leave_consistent_state(self) -> None:
        gen_eval, planned = self.runs["gen-eval"], self.runs["plan-gen-eval"]
        for run in (gen_eval, planned):
            self.assertEqual(execute("kb ask deletion", run / "project")[0], 0)
            self.assertEqual(execute("kb test", run / "project"), (0, "Ran 3 tests: OK"))
        self.assertTrue((gen_eval / "project" / "config" / "retrieval-notes.md").exists())
        self.assertFalse((planned / "project" / "config" / "retrieval-notes.md").exists())
        self.assertEqual(changed_paths(planned / "project"), ["kb/kb.py", "kb/test_kb.py"])

    def test_delete_and_import_are_not_started_in_the_app(self) -> None:
        self.assertFalse(hasattr(kb, "delete"))
        self.assertFalse(hasattr(kb, "import_document"))
        with fresh_project() as project:
            self.assertEqual(run_kb(project, "delete", "team-meeting"), (2, "error: delete is not implemented yet"))
            self.assertEqual(run_kb(project, "import", "x.md"), (2, "error: import is not implemented yet"))

    def test_the_next_session_inherits_the_record(self) -> None:
        # Without a doctor, session 2 trusts session 1's record; the doctor refuses it.
        project = self.runs["single-role"] / "project"
        failing = {check.name for check in doctor(project, project) if not check.passed}
        self.assertIn("evidence-reproduces:delete-command", failing)
        self.assertIn("handoff-sections", failing)

    def test_maker_writes_real_code(self) -> None:
        project = self.runs["single-role"] / "project"
        self.assertIn(BUGGY_DELETE, (project / "kb" / "kb.py").read_text(encoding="utf-8"))
        self.assertEqual(changed_paths(project), ["config/retrieval-notes.md", "kb/kb.py"])

    def test_scope_comes_from_git_not_the_transcript(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            run = build_run("plan-gen-eval", Path(temp))
            events = json.loads((run / "transcript.json").read_text(encoding="utf-8"))
            honest = {check.name: check.passed for check in score_run(run)}["scope-fidelity"]
            stripped = [event for event in events if event["type"] != "edit"]
            (run / "transcript.json").write_text(json.dumps(stripped), encoding="utf-8")
            self.assertEqual({check.name: check.passed for check in score_run(run)}["scope-fidelity"], honest)
            (run / "project" / "notes.md").write_text("silent change\n", encoding="utf-8")
            silent = {check.name: check for check in score_run(run)}["scope-fidelity"]
            self.assertFalse(silent.passed)
            self.assertIn("notes.md", silent.detail)

    def _solution_dirs(self) -> dict[int, Path]:
        return {module: check.SOLUTION_DIR for module, check in MODULE_CHECKS.items()}

    def test_solutions_reproduce_the_ladder(self) -> None:
        predicates, sources = load_predicates(self._solution_dirs())
        self.assertTrue(all(source.startswith("yours") for source in sources.values()), sources)
        scores = [sum(c.passed for c in score_run(self.runs[config], predicates)) for config in CONFIGS]
        self.assertEqual(scores, [0, 4, 5])

    def test_lenient_starter_check_moves_a_rung(self) -> None:
        dirs = self._solution_dirs()
        dirs[3] = EXERCISE_DIRS[3]
        predicates, sources = load_predicates(dirs)
        self.assertTrue(sources["clean-state"].startswith("yours"))
        checks = {check.name: check for check in score_run(self.runs["single-role"], predicates)}
        self.assertTrue(checks["clean-state"].passed, "starter readiness accepts the maker's handoff")

    def test_unimplemented_starter_functions_fall_back(self) -> None:
        _, sources = load_predicates(EXERCISE_DIRS)
        self.assertIn("not implemented", sources["scope-fidelity"])
        self.assertIn("not implemented", sources["findings-addressed"])
        _, empty = load_predicates({})
        self.assertTrue(all("file missing" in source for source in empty.values()))

    def test_stretch_starters_unimplemented_and_solutions_pass(self) -> None:
        for module, check in MODULE_CHECKS.items():
            starter = check.check_stretch(check.EXERCISE_DIR)
            solution = check.check_stretch(check.SOLUTION_DIR)
            self.assertEqual([item.detail for item in starter], ["not implemented yet"])
            self.assertTrue(all(item.passed for item in solution), f"module {module} stretch failed")

    def test_broken_exercise_code_is_reported_not_raised(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            (base / m3_check.CODE).write_text("def parse_handoff(text:\n", encoding="utf-8")
            (base / "session-handoff.md").write_text("# Handoff\n", encoding="utf-8")
            contract = m3_check.check(base)[0]
            self.assertFalse(contract.passed)
            self.assertIn("SyntaxError", contract.detail)

    def test_guard_suite_mutation_testing(self) -> None:
        solution = {check.name: check for check in m4_check.check_cases(m4_check.SOLUTION_DIR)}
        self.assertTrue(all(check.passed for check in solution.values()), solution)
        starter = {check.name: check for check in m4_check.check_cases(m4_check.EXERCISE_DIR)}
        self.assertTrue(starter["cases-agree-with-reference"].passed, "the starter's cases are right, just one-sided")
        survivors = starter["cases-catch-mutants"].detail.split(": ", 1)[1].split(", ")
        self.assertEqual(set(survivors), set(m4_check.MUTANTS) - {"allows everything"})

    def test_reference_guard_and_solution_agree(self) -> None:
        decide = load_exercise(m4_check.SOLUTION_DIR / m4_check.CODE).decide
        for case in load_json(m4_check.SOLUTION_DIR / m4_check.CASES):
            with self.subTest(case["label"]):
                event, plan = m4_check.event_for(case), m4_check.plan_for(case)
                self.assertEqual(decide(event, m4_check.PROJECT, plan)[0], m4_check.judge(event, m4_check.PROJECT, plan)[0])

    def test_lint_flags_the_scripted_makers_real_bug(self) -> None:
        lint = load_exercise(m2_check.SOLUTION_DIR / m2_check.CODE).lint_derived_state
        self.assertEqual([message.split("()")[0] for message in lint(BUGGY_DELETE)], ["delete"])
        self.assertEqual(lint(FIXED_DELETE), [])

    def test_contract_failures_name_the_case(self) -> None:
        check = contract_check("demo", [1, 0, 3], [1, 2, 4])
        self.assertEqual(check.detail, "failing case(s) 2, 3 of 3")

    def test_finding_needs_fix_then_passing_verification(self) -> None:
        events = [
            {"turn": 1, "role": "checker", "type": "finding", "id": "a"},
            {"turn": 2, "role": "maker", "type": "fix", "id": "a"},
        ]
        self.assertEqual(open_findings(events), ["a"])
        events.append({"turn": 3, "role": "checker", "type": "verification", "exit": 0})
        self.assertEqual(open_findings(events), [])
