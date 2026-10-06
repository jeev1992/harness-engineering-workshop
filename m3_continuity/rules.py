"""Module 3 harness rules: a fresh session can resume from the repository alone.

Builds on Module 2's evidence rules: the doctor re-executes recorded evidence
before any work begins.
"""

from __future__ import annotations

import re
from pathlib import Path

from m2_executable_verification.rules import validate_evidence
from shared.checks import Check

REQUIRED_HANDOFF_ORDER = ("Verified now", "Broken or unverified", "Next best step")


def parse_handoff(text: str) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("## "):
            current = line[3:].strip()
            sections[current] = []
        elif current is not None and line.startswith("- "):
            sections[current].append(line[2:].strip())
    return sections


def resume_ready(text: str) -> dict[str, object]:
    """Required sections must exist and carry at least one item (the Module 3 exercise reference)."""
    sections = parse_handoff(text)
    missing = [name for name in REQUIRED_HANDOFF_ORDER if not sections.get(name)]
    return {"ready": not missing, "missing": missing}


def validate_handoff(path: Path) -> list[Check]:
    report = resume_ready(path.read_text(encoding="utf-8"))
    missing = report["missing"]
    return [
        Check(
            "handoff-sections",
            bool(report["ready"]),
            f"missing or empty: {', '.join(missing) or 'none'}",
            fix=f"in {path.name}, give each of these a '## ' heading with at least one '- ' item: "
            f"{', '.join(missing)}",
        )
    ]


def validate_router(path: Path) -> list[Check]:
    """Every local link in the agent router (AGENTS.md) points at a file that exists."""
    if not path.is_file():
        return [
            Check(
                "router-targets", False, f"no {path.name}",
                fix=f"add a short {path.name} that points to the product docs, the feature list, and the handoff",
            )
        ]
    text = path.read_text(encoding="utf-8")
    targets = [
        target.split("#", 1)[0]
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text)
        if not target.startswith(("http://", "https://", "#"))
    ]
    missing = [target for target in targets if target and not (path.parent / target).exists()]
    return [
        Check(
            "router-targets",
            not missing,
            f"missing: {', '.join(missing) or 'none'}",
            fix=f"create the missing files or correct their links in {path.name}",
        )
    ]


def doctor(repository: Path, project: Path) -> list[Check]:
    """Startup checks a fresh session runs before selecting work."""
    features = repository / "feature_list.json"
    handoff = repository / "session-handoff.md"
    return [
        *validate_router(repository / "AGENTS.md"),
        *(validate_evidence(features, project) if features.is_file() else [
            Check("known-statuses", False, "no feature_list.json", fix="create feature_list.json: one entry per feature")
        ]),
        *(validate_handoff(handoff) if handoff.is_file() else [
            Check("handoff-sections", False, "no session-handoff.md", fix="write session-handoff.md before ending a session")
        ]),
    ]
