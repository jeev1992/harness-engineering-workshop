"""Throwaway copies of the kb project, run as real processes and tracked by git.

Every scripted run, and every check that needs a knowledge base, works in its
own copy of kb/ so the maker's edits are real file edits, verification runs
the project's own code in a separate process, and scope is read from git.
You never need to edit this file.
"""

from __future__ import annotations

import os
import shutil
import stat
import subprocess
import sys
import tempfile
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from pathlib import Path

from shared.checks import ROOT

DATA = "data"
# Work-tracking files every session is expected to update. Scope applies to the
# work itself, so these never count as changes. plan.json is not on this list:
# the planner commits it, and anyone else changing it is a scope violation.
STATE_FILES = ("feature_list.json", "session-handoff.md")
# Explicit identity and settings so commits work the same on every machine.
GIT = [
    "git",
    "-c", "user.name=workshop",
    "-c", "user.email=workshop@example.invalid",
    "-c", "commit.gpgsign=false",
    "-c", "core.autocrlf=false",
    "-c", "init.defaultBranch=main",
]


def remove_tree(path: Path) -> None:
    """Delete a previous run. Git marks its object files read-only, which Windows refuses to delete."""

    def make_writable_and_retry(function: Callable[[str], object], target: str, _: BaseException) -> None:
        os.chmod(target, stat.S_IWRITE)
        function(target)

    if path.exists():
        shutil.rmtree(path, onexc=make_writable_and_retry)


def git(project: Path, *args: str) -> str:
    return subprocess.run(
        [*GIT, *args], cwd=project, capture_output=True, text=True, encoding="utf-8", check=True
    ).stdout


def init_git(project: Path, message: str = "baseline") -> None:
    if shutil.which("git") is None:
        raise RuntimeError("git is required: install Git and make sure `git` is on PATH")
    git(project, "init", "-q")
    commit(project, message)


def create_project(path: Path, *, git: bool = False) -> Path:
    """Copy kb/ into path, seed its data directory, and optionally commit a git baseline."""
    from kb import kb  # imported here so a vendored copy of the harness never needs the app

    shutil.copytree(ROOT / "kb", path / "kb", ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    (path / ".gitignore").write_text(f"{DATA}/\n__pycache__/\n", encoding="utf-8")
    kb.init(path / DATA, path / "kb" / "seed")
    if git:
        init_git(path)
    return path


@contextmanager
def fresh_project() -> Iterator[Path]:
    """A seeded copy of the kb project in a throwaway directory."""
    with tempfile.TemporaryDirectory() as temp:
        yield create_project(Path(temp) / "project")


def run_python(project: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    """Run `python <args>` as a separate process inside the project."""
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONIOENCODING": "utf-8"}
    return subprocess.run(
        [sys.executable, *args],
        cwd=project,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
        check=False,
    )


def run_kb(project: Path, *args: str) -> tuple[int, str]:
    """Run the project's own kb command line: python kb/kb.py data <args>."""
    result = run_python(project, ["kb/kb.py", DATA, *args])
    return result.returncode, result.stdout.rstrip("\n")


def commit(project: Path, message: str) -> None:
    """Commit everything in the project, for example the planner's plan.json."""
    git(project, "add", "-A")
    git(project, "commit", "-q", "--allow-empty", "-m", message)


def scope_base(project: Path) -> str | None:
    """The planner's commit: the last one that touched plan.json. Scope is measured from there,
    so a maker that commits its own work cannot hide it from the check."""
    sha = git(project, "log", "-1", "--format=%H", "--", "plan.json").strip()
    return sha or None


def changed_paths(project: Path, since: str | None = None) -> list[str]:
    """Every path changed since a commit (default: the last one), including untracked files.

    The work-tracking STATE_FILES are left out: updating them is part of every session.
    """
    if since:
        tracked = git(project, "diff", "--name-only", "-z", since).split("\0")
        untracked = git(project, "ls-files", "--others", "--exclude-standard", "-z").split("\0")
        return sorted({path for path in [*tracked, *untracked] if path} - set(STATE_FILES))
    output = git(project, "status", "--porcelain=v1", "-z", "--untracked-files=all")
    entries = output.split("\0")
    paths: set[str] = set()
    index = 0
    while index < len(entries):
        entry = entries[index]
        index += 1
        if not entry:
            continue
        status, path = entry[:2], entry[3:]
        paths.add(path)
        if "R" in status or "C" in status:
            index += 1  # renames and copies carry the original path as an extra entry
    return sorted(paths - set(STATE_FILES))
