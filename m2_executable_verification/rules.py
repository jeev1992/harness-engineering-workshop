"""Module 2 harness rules: a passing status must be backed by evidence that reproduces.

Builds on Module 1's feature-state rules.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from pathlib import Path

from m1_scope_and_state.rules import validate_features
from shared.checks import Check, load_json
from shared.project import DATA, run_python

QUESTION = "How must deletion update state?"

# Planner-owned acceptance checks. Each runs the project's own code end to end
# in a throwaway copy of the seed data, so it proves the behavior, not the state.
_ACCEPTANCE_PRELUDE = """
import contextlib, io, sys, tempfile
from pathlib import Path
from kb import kb
def run(*args):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = kb.main([str(a) for a in args])
    return code, out.getvalue().strip()
def cited(data, question):
    try:
        return [c["document"] for c in kb.ask(data, question)["citations"]]
    except ValueError as error:
        return [f"error: {error}"]
"""
DELETE_ROUNDTRIP = _ACCEPTANCE_PRELUDE + """
with tempfile.TemporaryDirectory() as temp:
    data = Path(temp)
    kb.init(data, Path("kb/seed"))
    code, output = run(data, "delete", "team-meeting")
    files = sorted(p.name for p in (data / "documents").iterdir())
    ids = [d["id"] for d in kb.list_documents(data)["documents"]]
    answer = cited(data, "How must deletion update state?")
    ok = code == 0 and "team-meeting.txt" not in files and "team-meeting" not in ids and answer and "error" not in answer[0]
    print(f"delete exit {code}; files: {', '.join(files)}; indexed: {', '.join(ids)}; ask cites: {', '.join(answer) or 'nothing'}"
          + ("" if code == 0 else f"; output: {output}"))
    sys.exit(0 if ok else 1)
"""
IMPORT_ROUNDTRIP = _ACCEPTANCE_PRELUDE + """
with tempfile.TemporaryDirectory() as temp:
    data = Path(temp) / "data"
    kb.init(data, Path("kb/seed"))
    source = Path(temp) / "release-notes.md"
    source.write_text("# Release Notes\\n\\nImported documents must appear in the index immediately.\\n", encoding="utf-8")
    code, output = run(data, "import", source)
    files = sorted(p.name for p in (data / "documents").iterdir())
    ids = [d["id"] for d in kb.list_documents(data)["documents"]]
    answer = cited(data, "Where must imported documents appear?")
    ok = code == 0 and "release-notes.md" in files and "release-notes" in ids and answer[:1] == ["release-notes"]
    print(f"import exit {code}; indexed: {', '.join(ids)}; ask cites: {', '.join(answer) or 'nothing'}"
          + ("" if code == 0 else f"; output: {output}"))
    sys.exit(0 if ok else 1)
"""

# The only commands the harness accepts as evidence. Each runs as a separate
# process inside the project, so the observation comes from the project's own code.
VERIFICATION_COMMANDS: dict[str, list[str]] = {
    "kb list": ["kb/kb.py", DATA, "list"],
    "kb ask deletion": ["kb/kb.py", DATA, "ask", QUESTION],
    "kb test": ["-m", "unittest", "kb.test_kb"],
    "kb delete-roundtrip": ["-c", DELETE_ROUNDTRIP],
    "kb import-roundtrip": ["-c", IMPORT_ROUNDTRIP],
}


def describe(command: str) -> str:
    """The process a verification command runs, readable (inline scripts are summarized)."""
    args = VERIFICATION_COMMANDS[command]
    if args[0] == "-c":
        return f"python -c <{command.split()[-1]} acceptance script>"
    return " ".join(f'"{part}"' if " " in part else part for part in ["python", *args])


def _summarize_tests(stderr: str) -> str:
    """unittest prints timings; keep only the parts that reproduce exactly."""
    ran = re.search(r"^Ran \d+ tests?", stderr, flags=re.MULTILINE)
    lines = [line for line in stderr.strip().splitlines() if line.strip()]
    outcome = lines[-1] if lines else "no output"
    return f"{ran.group(0)}: {outcome}" if ran else f"tests did not run: {outcome}"


def execute(command: str, project: Path) -> tuple[int, str]:
    """Run one supported verification command in a project. Returns (exit, observed output)."""
    args = VERIFICATION_COMMANDS.get(command)
    if args is None:
        return 2, f"unsupported verification command: {command}"
    result = run_python(project, args)
    if command == "kb test":
        return result.returncode, _summarize_tests(result.stderr)
    return result.returncode, result.stdout.rstrip("\n")


def reproduce(feature: dict, run: Callable[[str], tuple[int, str]]) -> dict:
    """Re-execute recorded evidence and compare (the reference for the Module 2 exercise)."""
    evidence = feature.get("evidence", {})
    exit_code, observed = run(str(evidence.get("command", "")))
    return {
        "passed": exit_code == 0 and observed == evidence.get("observed"),
        "exit": exit_code,
        "observed": observed,
    }


def validate_evidence(feature_path: Path, project: Path) -> list[Check]:
    """Module 1's feature-state checks, plus re-execution of every passing feature's evidence."""
    checks = validate_features(feature_path)
    for feature in load_json(feature_path):
        if feature["status"] != "passing":
            continue
        command = str(feature.get("evidence", {}).get("command", ""))
        report = reproduce(feature, lambda recorded: execute(recorded, project))
        now = str(report["observed"])
        checks.append(
            Check(
                f"evidence-reproduces:{feature['id']}",
                report["passed"],
                "reproduced" if report["passed"] else "recorded evidence does not reproduce",
                fix=(
                    f"`{command}` now exits {report['exit']} with: {now[:160]}"
                    f"{'...' if len(now) > 160 else ''}. If that output is wrong, fix the code; "
                    "if it is right, record it as the evidence"
                    if command in VERIFICATION_COMMANDS
                    else f"use a supported verification command ({', '.join(VERIFICATION_COMMANDS)}) "
                    "and record its real output"
                ),
            )
        )
    return checks
