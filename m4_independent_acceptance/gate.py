"""
The done gate — Module 4
========================
One command that decides whether work on the kb project is done. It composes
the rules every module added, and runs them against the real repository:

    M1  feature state: known statuses, WIP=1, evidence on every passing feature
    M1  scope: a plan declares allowed_paths, and git shows nothing outside them
    M4  the work item: the planned feature is passing and the planner's
        acceptance command (for example `kb delete-roundtrip`) exits 0
    M2  evidence: every passing feature's recorded command reproduces now
    M2  tests: the project's own test suite passes
    M3  continuity: the handoff names what is verified, what is not, what is next

Every failure carries a fix line written for whoever acts next, person or
agent. In Module 4's Claude Code setup, a Stop hook runs this gate and refuses
to let the agent finish until it passes (hooks/stop_gate.py).

Run:
    python m4_independent_acceptance/gate.py <project>            # check a project
    python m4_independent_acceptance/gate.py <project> --explain  # why each control exists

Exits 0 when the work is done, 1 when it is not.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from m1_scope_and_state.rules import scope_violations
from m2_executable_verification.rules import VERIFICATION_COMMANDS, execute, validate_evidence
from m3_continuity.rules import validate_handoff
from shared.checks import Check, format_checks, load_json
from shared.project import changed_paths, scope_base


@dataclass(frozen=True)
class Control:
    """Why a control exists. Harnesses rot: each control should say when it can go."""

    module: str
    kind: str  # "contract": defines done, never expires. "compensating": works around a model weakness.
    exists_because: str
    remove_when: str


CONTROLS: dict[str, Control] = {
    "known-statuses": Control(
        "M1", "contract",
        "every tool that reads feature_list.json depends on a fixed set of statuses",
        "never: it is the file's schema",
    ),
    "wip-limit": Control(
        "M1", "compensating",
        "agents attempt too much at once and leave several features half-done (Module 1 starter)",
        "a frozen eval shows the agent finishes one feature before opening another without it",
    ),
    "passing-has-evidence": Control(
        "M1", "contract",
        "the baseline maker marked surviving-list passing with no evidence at all",
        "never: a passing status without evidence is a claim, not a fact",
    ),
    "evidence-reproduces": Control(
        "M2", "contract",
        "the baseline maker recorded 'exit 0: assumed' for a command that exits 1",
        "never: this is the definition of done",
    ),
    "scope-declared": Control(
        "M1", "compensating",
        "without a declared scope, an unrelated edit is indistinguishable from intended work",
        "the team stops caring which files a change touches (unlikely)",
    ),
    "planned-feature-done": Control(
        "M4", "contract",
        "every other control passes on a project where nothing was built yet; consistency is not completion",
        "never: the planner's acceptance command is what done means for this work item",
    ),
    "scope-fidelity": Control(
        "M4", "compensating",
        "the baseline maker edited config/retrieval-notes.md 'while in the area'",
        "evals show no out-of-scope edits across the task set, or the PreToolUse scope guard "
        "proves sufficient on its own (it cannot see shell edits, so check that first)",
    ),
    "tests-pass": Control(
        "M2", "contract",
        "a delete that breaks listing or answering must not count as done",
        "never",
    ),
    "handoff-sections": Control(
        "M3", "compensating",
        "the baseline maker's handoff said only 'Delete implemented and working'",
        "work never spans sessions, agents, or people, or the next session demonstrably resumes without it",
    ),
}


def control_for(check_name: str) -> Control | None:
    return CONTROLS.get(check_name.split(":", 1)[0])


def _required(path: Path, name: str, fix: str) -> Check | None:
    if path.is_file():
        return None
    return Check(name, False, f"{path.name} is missing", fix=fix)


def _planned_feature_done(plan: dict, features_path: Path, project: Path) -> Check:
    """The work item itself: its feature is passing and the planner's acceptance command exits 0."""
    feature, acceptance = plan.get("feature"), plan.get("acceptance")
    if not feature or acceptance not in VERIFICATION_COMMANDS:
        return Check(
            "planned-feature-done", False, "plan.json names no feature or no supported acceptance command",
            fix=f'the planner must set "feature" and "acceptance" (one of: {", ".join(VERIFICATION_COMMANDS)})',
        )
    statuses = {item.get("id"): item.get("status") for item in load_json(features_path)} if features_path.is_file() else {}
    exit_code, observed = execute(acceptance, project)
    passed = statuses.get(feature) == "passing" and exit_code == 0
    return Check(
        "planned-feature-done", passed,
        f"{feature} is {statuses.get(feature, 'missing')}; `{acceptance}` exits {exit_code}: {observed}",
        fix=f"make {feature} work end to end until `{acceptance}` exits 0, then mark it passing with real evidence",
    )


def gate(project: Path) -> list[Check]:
    """Run every control against a project. The work-tracking files live in the project root."""
    features = project / "feature_list.json"
    plan = project / "plan.json"
    handoff = project / "session-handoff.md"
    checks: list[Check] = []

    missing = _required(features, "known-statuses", "create feature_list.json: one entry per feature")
    checks.extend([missing] if missing else validate_evidence(features, project))

    if not plan.is_file():
        checks.append(
            Check(
                "scope-declared", False, "plan.json is missing",
                fix='a planner must commit plan.json with "allowed_paths" before the maker edits',
            )
        )
    else:
        allowed = load_json(plan).get("allowed_paths", [])
        checks.append(
            Check(
                "scope-declared", bool(allowed), f"allowed paths: {', '.join(allowed) or 'none'}",
                fix='plan.json "allowed_paths" must list the paths this work may change',
            )
        )
        changed = changed_paths(project, since=scope_base(project))
        violations = scope_violations(allowed, changed)
        checks.append(
            Check(
                "scope-fidelity", bool(allowed) and not violations,
                f"git shows out-of-scope changes: {', '.join(violations)}" if violations
                else f"git shows {len(changed)} change(s), all inside the declared scope",
                fix=f"revert {', '.join(violations)} (git checkout / delete untracked files), "
                "or stop and ask the planner to widen plan.json",
            )
        )
        checks.append(_planned_feature_done(load_json(plan), features, project))

    exit_code, observed = execute("kb test", project)
    checks.append(
        Check(
            "tests-pass", exit_code == 0, observed,
            fix="run `python -m unittest kb.test_kb`, read the failure, and fix the code (not the test)",
        )
    )

    missing = _required(handoff, "handoff-sections", "write session-handoff.md: verified now, broken or unverified, next best step")
    checks.extend([missing] if missing else validate_handoff(handoff))
    return checks


def explain() -> str:
    lines = ["Every control encodes an assumption. Contract controls define done; compensating", "controls work around a model weakness and should be removed when it is gone.", ""]
    for name, control in CONTROLS.items():
        lines.append(f"{name}  [{control.module}, {control.kind}]")
        lines.append(f"  exists because: {control.exists_because}")
        lines.append(f"  remove when:    {control.remove_when}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="The done gate for the kb project.")
    parser.add_argument("project", type=Path, nargs="?", default=Path.cwd())
    parser.add_argument("--explain", action="store_true", help="show why each control exists")
    args = parser.parse_args(argv)
    if args.explain:
        print(explain())
        return 0
    checks = gate(args.project.resolve())
    print(format_checks(checks))
    failing = [check for check in checks if not check.passed]
    print(f"\nDONE GATE: {'PASS' if not failing else f'FAIL ({len(failing)} of {len(checks)})'}")
    return 0 if not failing else 1


if __name__ == "__main__":
    raise SystemExit(main())
