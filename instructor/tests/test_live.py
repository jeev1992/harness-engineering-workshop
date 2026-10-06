"""Tests for the live Claude Code tooling: project generation, the vendored harness, and scoring.

Claude Code itself is not run here. A scripted, well-behaved agent stands in
for it, and the hooks are exercised through the same stdin/exit-code protocol
Claude Code uses.
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from instructor.live import score_project, setup_project
from shared.project import git
from shared.scenario import DELETE_TEST, FIXED_DELETE, add_before_main

STOP = ".harness/m4_independent_acceptance/hooks/stop_gate.py"
GUARD = ".harness/m1_scope_and_state/hooks/scope_guard.py"


def hook(project: Path, script: str, event: dict) -> int:
    return subprocess.run(
        [sys.executable, str(project / script)], input=json.dumps(event), capture_output=True, text=True,
        env={**os.environ, "CLAUDE_PROJECT_DIR": str(project)}, check=False,
    ).returncode


def quietly(function, *args):
    with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
        return function(*args)


class LiveProjectTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._temp = tempfile.TemporaryDirectory()
        base = Path(cls._temp.name)
        cls.off, cls.on = base / "live-off", base / "live-on"
        quietly(setup_project.main, [str(cls.off), "--harness", "off"])
        quietly(setup_project.main, [str(cls.on), "--harness", "on"])

    @classmethod
    def tearDownClass(cls) -> None:
        cls._temp.cleanup()

    def test_refuses_a_target_inside_the_workshop(self) -> None:
        with self.assertRaises(SystemExit):
            quietly(setup_project.main, [str(ROOT / "live-on"), "--harness", "on"])

    def test_bare_and_harnessed_differ_only_in_harness_files(self) -> None:
        off = set(git(self.off, "ls-files").split())
        on = set(git(self.on, "ls-files").split())
        self.assertLessEqual(off, on)
        self.assertTrue({"AGENTS.md", "CLAUDE.md", "plan.json", ".claude/settings.json"} <= on - off)
        self.assertEqual((self.on / "CLAUDE.md").read_text(encoding="utf-8").strip(), "@AGENTS.md")

    def test_settings_wire_both_hooks_in_exec_form(self) -> None:
        settings = json.loads((self.on / ".claude" / "settings.json").read_text(encoding="utf-8"))
        for event in ("PreToolUse", "Stop"):
            handler = settings["hooks"][event][0]["hooks"][0]
            self.assertEqual(handler["command"], sys.executable)
            self.assertTrue(handler["args"][0].startswith("${CLAUDE_PROJECT_DIR}/.harness/"))
        self.assertIn("Edit(/plan.json)", settings["permissions"]["deny"])

    def test_ablation_removes_exactly_one_control(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "no-stop"
            quietly(setup_project.main, [str(target), "--harness", "on", "--without", "stop-gate"])
            hooks = json.loads((target / ".claude" / "settings.json").read_text(encoding="utf-8"))["hooks"]
            self.assertEqual(set(hooks), {"PreToolUse"})

    def test_a_fresh_project_is_consistent_but_not_done(self) -> None:
        self.assertEqual(hook(self.on, STOP, {"hook_event_name": "Stop"}), 2)
        result = subprocess.run([sys.executable, ".harness/doctor.py"], cwd=self.on, capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_hidden_eval_gives_an_unbuilt_project_no_credit_for_edge_cases(self) -> None:
        results = score_project.hidden_eval(self.off)
        self.assertEqual([name for name, passed in results.items() if passed], ["the project's own tests pass"])

    def test_a_well_behaved_agent_is_released_and_a_hidden_edit_is_not(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp) / "agent"
            quietly(setup_project.main, [str(project), "--harness", "on"])
            self.assertEqual(hook(project, GUARD, {"tool_name": "Edit", "tool_input": {"file_path": str(project / "plan.json")}}), 2)

            kb_py, test_py = project / "kb" / "kb.py", project / "kb" / "test_kb.py"
            kb_py.write_text(add_before_main(FIXED_DELETE)(kb_py.read_text(encoding="utf-8")), encoding="utf-8")
            test_py.write_text(test_py.read_text(encoding="utf-8") + DELETE_TEST, encoding="utf-8")
            observed = json.loads(subprocess.run(
                [sys.executable, ".harness/observe.py", "kb delete-roundtrip"], cwd=project, capture_output=True, text=True, check=False,
            ).stdout)
            features = json.loads((project / "feature_list.json").read_text(encoding="utf-8"))
            for feature in features:
                if feature["id"] == "delete-command":
                    feature["status"] = "passing"
                    feature["evidence"] = {"command": observed["command"], "observed": observed["observed"]}
            (project / "feature_list.json").write_text(json.dumps(features), encoding="utf-8")
            self.assertEqual(hook(project, STOP, {"hook_event_name": "Stop"}), 0)
            self.assertTrue(all(score_project.hidden_eval(project).values()))

            # Committing an out-of-scope file does not hide it: scope is measured from the planner's commit.
            (project / "notes.md").write_text("x\n", encoding="utf-8")
            git(project, "add", "-A")
            git(project, "commit", "-q", "-m", "agent work")
            self.assertEqual(hook(project, STOP, {"hook_event_name": "Stop"}), 2)
