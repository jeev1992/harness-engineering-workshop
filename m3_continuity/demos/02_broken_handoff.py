"""
Demo 02 — What a broken handoff looks like
==========================================
A handoff is the note one session leaves for the next. Three handoffs, all
of which "look fine" to a human skimming them, judged by the readiness rule:
every required section must exist and carry at least one item.

Run:
    python m3_continuity/demos/02_broken_handoff.py

You will see:
    1. The baseline maker's handoff: one optimistic line
    2. An honest handoff with no next step (the exercise starter's defect)
    3. A complete handoff, including an extra section the rule ignores
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from m3_continuity.rules import parse_handoff, resume_ready

HANDOFFS = {
    "optimistic": "# Session handoff\n\n## Verified now\n\n- Delete implemented and working.\n",
    "no next step": (
        "# Session handoff\n\n## Verified now\n\n- Document listing reproduces.\n\n"
        "## Broken or unverified\n\n- Delete has not been checked against the metadata index.\n"
    ),
    "complete": (
        "# Session handoff\n\n## Verified now\n\n- Document listing reproduces.\n\n"
        "## Broken or unverified\n\n- Delete has not been checked against the metadata index.\n\n"
        "## Next best step\n\n- Add a test that deletes one document and asserts the file "
        "and index entry are absent.\n\n"
        "## Risks\n\n- The index may already hold dangling entries.\n"
    ),
}


def main() -> None:
    for label, text in HANDOFFS.items():
        report = resume_ready(text)
        sections = ", ".join(parse_handoff(text)) or "none"
        print(f"{label}")
        print(f"  sections: {sections}")
        print(f"  ready:    {report['ready']}  missing or empty: {', '.join(report['missing']) or 'none'}\n")
    print("Strict about required sections, tolerant of additional ones: 'Risks' survives")
    print("parsing without being required.")


if __name__ == "__main__":
    main()
