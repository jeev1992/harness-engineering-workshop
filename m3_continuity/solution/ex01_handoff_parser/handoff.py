"""Module 3 exercise — the handoff parser (reference solution).

Check: python m3_continuity/exercises/check.py --solution
"""

from __future__ import annotations

REQUIRED = ("Verified now", "Broken or unverified", "Next best step")


def parse_handoff(text: str) -> dict[str, list[str]]:
    """Parse handoff sections without dropping unknown sections."""
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
    """Report whether a fresh session has the required handoff sections."""
    sections = parse_handoff(text)
    missing = [name for name in REQUIRED if name not in sections or not sections[name]]
    return {"ready": not missing, "missing": missing}


# Stretch: write handoffs that round-trip through your own parser.


def render_handoff(title: str, sections: dict[str, list[str]]) -> str:
    """Render a handoff that parse_handoff reads back unchanged.

    Section order is preserved, empty sections survive, and the text ends
    with exactly one newline.
    """
    lines = [f"# {title}"]
    for name, items in sections.items():
        lines.extend(["", f"## {name}"])
        if items:
            lines.append("")
            lines.extend(f"- {item}" for item in items)
    return "\n".join(lines) + "\n"
