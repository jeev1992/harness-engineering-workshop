"""Plumbing shared by every module's check script. You never need to edit this file."""

from __future__ import annotations

import argparse
import importlib.util
import json
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "kb" / "seed"


@dataclass(frozen=True)
class Check:
    name: str
    passed: bool
    detail: str
    # Remediation for a failure, written for whoever acts next (a person or an agent).
    fix: str = ""


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def format_checks(checks: list[Check]) -> str:
    lines = []
    for check in checks:
        lines.append(f"{'PASS' if check.passed else 'FAIL'} {check.name}: {check.detail}")
        if not check.passed and check.fix:
            lines.append(f"     fix: {check.fix}")
    return "\n".join(lines)


def print_checks(checks: list[Check]) -> bool:
    print(format_checks(checks))
    return all(check.passed for check in checks)


def guarded(name: str, run: Callable[[], Check]) -> Check:
    """Exercise code is mid-edit during class; report failures instead of crashing."""
    try:
        return run()
    except NotImplementedError:
        return Check(name, False, "not implemented yet")
    except Exception as error:
        return Check(name, False, f"{type(error).__name__}: {error}")


def contract_check(name: str, results: list, expected: list) -> Check:
    failing = [
        str(index)
        for index, (result, wanted) in enumerate(zip(results, expected, strict=True), 1)
        if result != wanted
    ]
    if not failing:
        return Check(name, True, f"all {len(expected)} contract cases pass")
    return Check(name, False, f"failing case(s) {', '.join(failing)} of {len(expected)}")


def load_exercise(path: Path) -> ModuleType:
    """Import an exercise file by path, fresh each time."""
    spec = importlib.util.spec_from_file_location(f"exercise_{path.parent.name}_{path.stem}", path)
    if spec is None or spec.loader is None:
        raise ValueError(f"cannot load exercise: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_check_cli(
    *,
    exercise_dir: Path,
    solution_dir: Path,
    edit: list[str],
    check: Callable[[Path], list[Check]],
    check_stretch: Callable[[Path], list[Check]],
) -> None:
    """Command line shared by every exercises/check.py."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--stretch", action="store_true", help="check the optional stretch task")
    parser.add_argument("--solution", action="store_true", help="check the reference solution")
    args = parser.parse_args()
    base = solution_dir if args.solution else exercise_dir
    checks = check_stretch(base) if args.stretch else check(base)
    passed = print_checks(checks)
    if passed:
        print(f"\nPassed: {len(checks)} of {len(checks)}.")
        raise SystemExit(0)
    failing = sum(not item.passed for item in checks)
    print(f"\nFailing: {failing} of {len(checks)}.")
    if not args.solution:
        relative = exercise_dir.relative_to(ROOT).as_posix()
        print("Edit:  " + "\n       ".join(f"{relative}/{name}" for name in edit))
    raise SystemExit(1)
