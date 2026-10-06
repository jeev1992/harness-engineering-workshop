"""Module 3 exercise — the handoff parser.

Brief: m3_continuity/exercises/ex01_handoff_parser.md
Check: python m3_continuity/exercises/check.py
"""

from __future__ import annotations


def parse_handoff(text: str) -> dict[str, list[str]]:
    """Parse handoff sections without dropping unknown sections."""
    return {}


def resume_ready(text: str) -> dict[str, object]:
    """Report whether a fresh session has the required handoff sections."""
    return {"ready": bool(text), "missing": []}


# Stretch: write handoffs that round-trip through your own parser.


def render_handoff(title: str, sections: dict[str, list[str]]) -> str:
    """Render a handoff that parse_handoff reads back unchanged.

    Section order is preserved, empty sections survive, and the text ends
    with exactly one newline.
    """
    raise NotImplementedError
