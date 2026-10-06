"""Two-sided tests for the in-loop harness: the scope guard, the done gate, and the stop gate.

Every guard is tested in both directions. A guard that is only tested on what
it must block can drift toward blocking everything without any test noticing.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from m1_scope_and_state.hooks import scope_guard
from m4_independent_acceptance import gate as done_gate
from m4_independent_acceptance.hooks import stop_gate
from shared.project import commit, create_project, remove_tree
from m2_executable_verification.rules import execute
from shared.scenario import IMPORT_SOURCE, PLAN_SCOPE, add_before_main, build_runs

ALLOW, BLOCK = 0, 2


def edit(tool: str, path: Path | str, key: str = "file_path") -> dict:
    return {"hook_event_name": "PreToolUse", "tool_name": tool, "tool_input": {key: str(path)}}


class ScopeGuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._temp = tempfile.TemporaryDirectory()
        cls.project = create_project(Path(cls._temp.name) / "project", git=True)
        (cls.project / "plan.json").write_text(
            json.dumps({"allowed_paths": ["kb/kb.py", "kb/test_kb.py", "docs/"]}), encoding="utf-8"
        )
        commit(cls.project, "plan")

    @classmethod
    def tearDownClass(cls) -> None:
        cls._temp.cleanup()

    def verdict(self, event: dict, project: Path | None = None) -> int:
        return scope_guard.decide(event, project or self.project)[0]

    def test_must_allow(self) -> None:
        project = self.project
        cases = {
            "in-scope edit": edit("Edit", project / "kb" / "kb.py"),
            "in-scope write": edit("Write", project / "kb" / "test_kb.py"),
            "inside a scoped directory": edit("Write", project / "docs" / "deep" / "delete.md"),
            "forward slashes": edit("Edit", str(project / "kb" / "kb.py").replace("\\", "/")),
            "feature list state": edit("Write", project / "feature_list.json"),
            "handoff state": edit("Edit", project / "session-handoff.md"),
            "notebook in scope": edit("NotebookEdit", project / "docs" / "n.ipynb", key="notebook_path"),
            "read anything": edit("Read", project / "config" / "secret.md"),
            "shell command": {"tool_name": "Bash", "tool_input": {"command": "echo x > notes.md"}},
        }
        if os.name == "nt":
            cases["different letter case"] = edit("Edit", str(project / "KB" / "KB.PY").upper())
        for label, event in cases.items():
            with self.subTest(label):
                self.assertEqual(self.verdict(event), ALLOW)

    def test_must_block(self) -> None:
        project = self.project
        cases = {
            "unrelated file": edit("Write", project / "config" / "retrieval-notes.md"),
            "its own plan": edit("Edit", project / "plan.json"),
            "lookalike name": edit("Write", project / "kb" / "kb.py.bak"),
            "directory prefix trick": edit("Write", project / "docs_extra" / "x.md"),
            "path traversal": edit("Write", str(project / "kb" / ".." / "config" / "x.md")),
            "outside the project": edit("Write", project.parent / "elsewhere.txt"),
            "empty path": edit("Write", ""),
        }
        for label, event in cases.items():
            with self.subTest(label):
                code, message = scope_guard.decide(event, project)
                self.assertEqual(code, BLOCK)
                self.assertTrue(message.startswith("Blocked:"), message)

    def test_blocks_every_edit_until_a_plan_exists(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            unplanned = create_project(Path(temp) / "project")
            self.assertEqual(self.verdict(edit("Edit", unplanned / "kb" / "kb.py"), unplanned), BLOCK)
            self.assertEqual(self.verdict(edit("Write", unplanned / "feature_list.json"), unplanned), ALLOW)

    def test_speaks_the_claude_code_protocol(self) -> None:
        hook = ROOT / "m1_scope_and_state" / "hooks" / "scope_guard.py"
        env = {**os.environ, "CLAUDE_PROJECT_DIR": str(self.project)}
        for path, expected in ((self.project / "kb" / "kb.py", ALLOW), (self.project / "x.md", BLOCK)):
            with self.subTest(expected=expected):
                result = subprocess.run(
                    [sys.executable, str(hook)], input=json.dumps(edit("Write", path)),
                    capture_output=True, text=True, env=env, check=False,
                )
                self.assertEqual(result.returncode, expected)
                self.assertEqual(bool(result.stderr.strip()), expected == BLOCK)


class GateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._temp = tempfile.TemporaryDirectory()
        cls.runs = build_runs(Path(cls._temp.name))

    @classmethod
    def tearDownClass(cls) -> None:
        cls._temp.cleanup()

    def copy(self, config: str) -> Path:
        target = Path(self._temp.name) / f"copy-{config}-{self.id().rsplit('.', 1)[-1]}"
        remove_tree(target)
        shutil.copytree(self.runs[config] / "project", target)
        return target

    def failing(self, project: Path) -> dict:
        return {check.name: check for check in done_gate.gate(project) if not check.passed}

    def test_passes_the_finished_planned_run(self) -> None:
        self.assertEqual(self.failing(self.runs["plan-gen-eval"] / "project"), {})

    def test_fails_the_baseline_with_a_fix_for_every_failure(self) -> None:
        failing = self.failing(self.runs["single-role"] / "project")
        self.assertEqual(
            set(failing),
            {
                "passing-has-evidence",
                "evidence-reproduces:delete-command",
                "evidence-reproduces:surviving-list",
                "scope-declared",
                "handoff-sections",
            },
        )
        for check in failing.values():
            self.assertTrue(check.fix, f"{check.name} has no fix line")

    def test_the_baselines_tests_pass_yet_the_gate_still_fails(self) -> None:
        checks = {check.name: check for check in done_gate.gate(self.runs["single-role"] / "project")}
        self.assertTrue(checks["tests-pass"].passed, "the maker wrote no delete test")
        self.assertFalse(checks["evidence-reproduces:delete-command"].passed)

    def test_catches_a_maker_that_widens_its_own_plan(self) -> None:
        project = self.copy("plan-gen-eval")
        plan = project / "plan.json"
        widened = {**json.loads(plan.read_text(encoding="utf-8")), "allowed_paths": [*PLAN_SCOPE, "config/"]}
        plan.write_text(json.dumps(widened), encoding="utf-8")
        failing = self.failing(project)
        self.assertIn("scope-fidelity", failing)
        self.assertIn("plan.json", failing["scope-fidelity"].detail)

    def test_catches_an_edit_the_guard_cannot_see(self) -> None:
        project = self.copy("plan-gen-eval")
        (project / "notes.md").write_text("written by a shell command\n", encoding="utf-8")
        self.assertIn("notes.md", self.failing(project)["scope-fidelity"].detail)

    def test_fails_without_a_handoff(self) -> None:
        project = self.copy("plan-gen-eval")
        (project / "session-handoff.md").unlink()
        self.assertIn("handoff-sections", self.failing(project))

    def test_every_control_records_why_it_exists(self) -> None:
        names = {check.name for config in self.runs for check in done_gate.gate(self.runs[config] / "project")}
        for name in names:
            with self.subTest(name):
                control = done_gate.control_for(name)
                self.assertIsNotNone(control, f"{name} has no entry in CONTROLS")
                self.assertIn(control.kind, {"contract", "compensating"})

    def test_consistency_is_not_completion(self) -> None:
        # A planned project where nothing was built yet passes every control except the work item.
        with tempfile.TemporaryDirectory() as temp:
            project = create_project(Path(temp) / "project", git=True)
            (project / "plan.json").write_text(json.dumps({
                "feature": "delete-command", "acceptance": "kb delete-roundtrip", "allowed_paths": PLAN_SCOPE,
            }), encoding="utf-8")
            (project / "feature_list.json").write_text(json.dumps([
                {"id": "delete-command", "status": "in-progress", "evidence": {}},
            ]), encoding="utf-8")
            (project / "session-handoff.md").write_text(
                "# H\n\n## Verified now\n\n- x\n\n## Broken or unverified\n\n- y\n\n## Next best step\n\n- z\n",
                encoding="utf-8",
            )
            commit(project, "plan")
            failing = self.failing(project)
            self.assertEqual(set(failing), {"planned-feature-done"})
            self.assertIn("delete is not implemented yet", failing["planned-feature-done"].detail)

    def test_acceptance_commands_judge_behavior(self) -> None:
        cases = {
            ("single-role", "kb delete-roundtrip"): 1,
            ("plan-gen-eval", "kb delete-roundtrip"): 0,
            ("plan-gen-eval", "kb import-roundtrip"): 1,
        }
        for (config, command), expected in cases.items():
            with self.subTest(config=config, command=command):
                self.assertEqual(execute(command, self.runs[config] / "project")[0], expected)
        project = self.copy("plan-gen-eval")
        (project / "kb" / "kb.py").write_text(
            add_before_main(IMPORT_SOURCE)((project / "kb" / "kb.py").read_text(encoding="utf-8")), encoding="utf-8"
        )
        self.assertEqual(execute("kb import-roundtrip", project)[0], 0)

    def test_stop_gate_blocks_the_baseline_and_releases_the_finished_run(self) -> None:
        code, message = stop_gate.decide({"hook_event_name": "Stop"}, self.runs["single-role"] / "project")
        self.assertEqual(code, BLOCK)
        self.assertIn("fix:", message)
        self.assertEqual(stop_gate.decide({"hook_event_name": "Stop"}, self.runs["plan-gen-eval"] / "project"), (ALLOW, ""))

    def test_stop_gate_speaks_the_claude_code_protocol(self) -> None:
        hook = ROOT / "m4_independent_acceptance" / "hooks" / "stop_gate.py"
        for config, expected in (("single-role", BLOCK), ("plan-gen-eval", ALLOW)):
            with self.subTest(config):
                project = self.runs[config] / "project"
                result = subprocess.run(
                    [sys.executable, str(hook)],
                    input=json.dumps({"hook_event_name": "Stop", "stop_hook_active": False, "cwd": str(project)}),
                    capture_output=True, text=True,
                    env={**os.environ, "CLAUDE_PROJECT_DIR": str(project)}, check=False,
                )
                self.assertEqual(result.returncode, expected, result.stderr)
