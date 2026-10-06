"""Module 4 harness rules: planning, making, and accepting are separate roles.

The done gate (gate.py) composes every module's rules; this file holds the
findings rule the checker uses to decide when a finding is closed.
"""

from __future__ import annotations


def open_findings(events: list[dict]) -> list[str]:
    """A finding is closed only by a later fix and a passing verification after that fix."""
    still_open: set[str] = set()
    for finding in (event for event in events if event["type"] == "finding"):
        fix_turns = [
            event["turn"]
            for event in events
            if event["type"] == "fix"
            and event.get("id") == finding.get("id")
            and event["turn"] > finding["turn"]
        ]
        verified = bool(fix_turns) and any(
            event["type"] == "verification"
            and event.get("exit") == 0
            and event["turn"] > min(fix_turns)
            for event in events
        )
        if not verified:
            still_open.add(str(finding.get("id")))
    return sorted(still_open)
