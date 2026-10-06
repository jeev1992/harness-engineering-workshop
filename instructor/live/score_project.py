"""
Instructor: score live Claude Code runs side by side
====================================================
Two separate questions, kept separate on purpose:

    hidden eval   Did the work actually work? Five behavioral cases the agent
                  never saw, run against the project's own code in a throwaway
                  copy of the seed data. This is the fair comparison between a
                  bare run and a harnessed run.
    done gate     Could the repository prove it? The same gate the Stop hook
                  runs. A bare project has no plan, feature list, or handoff,
                  so it fails here even when the code works.

It also lists what changed since the baseline commit (agent commits included),
and, given a Claude Code stream-json transcript, which tools the agent used.

Run:
    python instructor/live/score_project.py ../live-off ../live-on
    python instructor/live/score_project.py ../live-on --transcript ../live-on.jsonl

Two runs are a demo, not an eval. An eval freezes 20 to 50 tasks and changes
one control at a time.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from m2_executable_verification.rules import execute
from m4_independent_acceptance.gate import gate
from shared.project import changed_paths, git, run_python

WORK_SCOPE = {"kb/kb.py", "kb/test_kb.py"}
HIDDEN_EVAL = """
import contextlib, io, json, sys, tempfile
from pathlib import Path
from kb import kb

def run(*args):
    out = io.StringIO()
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            return kb.main([str(a) for a in args])
    except SystemExit as error:
        return error.code if isinstance(error.code, int) else 1
    except Exception:
        return 99  # an unhandled crash

def state(data):
    files = {p.name: p.read_text(encoding="utf-8") for p in (data / "documents").iterdir()}
    try:
        ids = [d["id"] for d in kb.list_documents(data)["documents"]]
    except Exception as error:
        ids = [f"error: {error}"]
    return files, ids

def answers(data):
    try:
        return bool(kb.ask(data, "How must deletion update state?")["citations"])
    except Exception:
        return False

results = {}
def case(name, check):
    with tempfile.TemporaryDirectory() as temp:
        data = Path(temp)
        kb.init(data, Path("kb/seed"))
        try:
            results[name] = bool(check(data))
        except Exception:
            results[name] = False

def removes_file_and_index_entry(data):
    code = run(data, "delete", "team-meeting")
    files, ids = state(data)
    return code == 0 and "team-meeting.txt" not in files and ids == ["architecture-notes", "retrieval-plan"] and answers(data)

def unknown_id_fails_cleanly(data):
    first = run(data, "delete", "retrieval-plan")  # delete must work at all, or this proves nothing
    before = state(data)
    code = run(data, "delete", "no-such-document")
    return first == 0 and code not in (0, 99) and state(data) == before

def second_delete_fails_cleanly(data):
    first = run(data, "delete", "team-meeting")
    after_first = state(data)
    code = run(data, "delete", "team-meeting")
    return first == 0 and code not in (0, 99) and state(data) == after_first

def other_documents_untouched(data):
    files_before, _ = state(data)
    run(data, "delete", "retrieval-plan")
    files, ids = state(data)
    return all(files.get(n) == files_before[n] for n in ("architecture-notes.md", "team-meeting.txt")) and ids == ["architecture-notes", "team-meeting"]

case("delete removes the file and its index entry; answers still work", removes_file_and_index_entry)
case("deleting an unknown id fails cleanly and changes nothing", unknown_id_fails_cleanly)
case("deleting twice fails cleanly the second time", second_delete_fails_cleanly)
case("other documents are untouched", other_documents_untouched)
print(json.dumps(results))
"""


def hidden_eval(project: Path) -> dict[str, bool]:
    result = run_python(project, ["-c", HIDDEN_EVAL])
    try:
        results = json.loads(result.stdout.strip().splitlines()[-1])
    except (IndexError, json.JSONDecodeError):
        results = {"hidden eval could not run": False}
    results["the project's own tests pass"] = execute("kb test", project)[0] == 0
    return results


def tool_tally(transcript: Path) -> str:
    """Tolerant read of a Claude Code stream-json transcript: count tool calls by tool name."""
    tools: Counter[str] = Counter()
    gate_runs = 0
    for line in transcript.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        content = (event.get("message") or {}).get("content") if isinstance(event, dict) else None
        for item in content if isinstance(content, list) else []:
            if isinstance(item, dict) and item.get("type") == "tool_use":
                tools[str(item.get("name"))] += 1
                if ".harness/gate.py" in json.dumps(item.get("input", {})):
                    gate_runs += 1
    if not tools:
        return "no tool calls found (is this a stream-json transcript?)"
    calls = ", ".join(f"{name} {count}" for name, count in tools.most_common())
    return f"{sum(tools.values())} tool calls ({calls}); ran the gate itself {gate_runs} time(s)"


def score(project: Path, transcript: Path | None) -> None:
    harnessed = (project / ".harness").is_dir()
    print(f"== {project}  ({'harness on' if harnessed else 'harness off'})")

    results = hidden_eval(project)
    print(f"hidden eval   {sum(results.values())}/{len(results)}  (did the work actually work?)")
    for name, passed in results.items():
        print(f"  {'PASS' if passed else 'FAIL'} {name}")

    checks = gate(project)
    failing = [check for check in checks if not check.passed]
    verdict = "PASS" if not failing else f"FAIL ({len(failing)} of {len(checks)})"
    print(f"done gate     {verdict}  (could the repository prove it?)")
    for check in failing:
        print(f"  FAIL {check.name}: {check.detail}")

    root = git(project, "rev-list", "--max-parents=0", "HEAD").split()[0]
    changed = changed_paths(project, since=root)
    outside = sorted(set(changed) - WORK_SCOPE)
    print(f"changed       {', '.join(changed) or 'nothing'}")
    if outside:
        print(f"  outside kb/kb.py and kb/test_kb.py: {', '.join(outside)}")
    if transcript:
        print(f"transcript    {tool_tally(transcript)}")
    print()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Score live Claude Code runs.")
    parser.add_argument("projects", type=Path, nargs="+")
    parser.add_argument("--transcript", type=Path, action="append", default=[],
                        help="stream-json transcript, in the same order as the projects")
    args = parser.parse_args(argv)
    transcripts = args.transcript + [None] * (len(args.projects) - len(args.transcript))
    for project, transcript in zip(args.projects, transcripts, strict=True):
        score(project.resolve(), transcript)
    print("Two runs are a demo, not an eval: an eval freezes 20-50 tasks and changes one control at a time.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
