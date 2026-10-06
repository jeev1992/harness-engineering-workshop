"""
Demo 02 — WIP=1 and declared scope, as checks
=============================================
"Only one thing in progress" and "declare what you will touch" are easy to
agree with and easy to fake. This demo turns both into checks over plain
repository files and shows the tempting shortcut that gets them wrong.

Run:
    python m1_scope_and_state/demos/02_wip_limit.py

You will see:
    1. Feature lists with zero, one, and two items in progress, judged by
       the shortcut `bool(active)` and by the real rule `len(active) <= 1`
    2. Plans judged by key presence versus a non-empty, usable scope
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from m1_scope_and_state.rules import validate_features, validate_plan

FEATURE_LISTS = {
    "nothing active": [{"id": "delete-command", "status": "not-started", "evidence": {}}],
    "one active": [{"id": "delete-command", "status": "in-progress", "evidence": {}}],
    "two active": [
        {"id": "delete-command", "status": "in-progress", "evidence": {}},
        {"id": "improve-retrieval", "status": "in-progress", "evidence": {}},
    ],
}
PLANS = {
    "empty scope": {"allowed_paths": [], "next_action": ""},
    "declared scope": {
        "allowed_paths": ["kb/kb.py", "kb/test_kb.py"],
        "next_action": "Add a failing test for removal from the document file and metadata index",
    },
}


def main() -> None:
    with tempfile.TemporaryDirectory() as temp:
        path = Path(temp) / "artifact.json"

        print("1. WIP limit")
        print(f"  {'feature list':<16}{'bool(active)':<15}{'len(active) <= 1'}")
        for label, features in FEATURE_LISTS.items():
            path.write_text(json.dumps(features), encoding="utf-8")
            active = [item for item in features if item["status"] == "in-progress"]
            rule = next(check for check in validate_features(path) if check.name == "wip-limit")
            print(f"  {label:<16}{str(bool(active)):<15}{str(rule.passed):<7}({rule.detail})")
        print("  The shortcut rejects an idle list and accepts two open items: it tests")
        print("  that work exists, not that work is bounded.\n")

        print("2. Declared scope")
        for label, plan in PLANS.items():
            path.write_text(json.dumps(plan), encoding="utf-8")
            print(f"  {label}: keys present = {'allowed_paths' in plan and 'next_action' in plan}")
            for check in validate_plan(path):
                print(f"    {'PASS' if check.passed else 'FAIL'} {check.name}: {check.detail}")
        print("  Key presence is not scope. A check must test that the value is usable.")


if __name__ == "__main__":
    main()
