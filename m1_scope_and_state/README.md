# Module 1 — Scope and state (`m1_scope_and_state`)

This module opens the workshop with the failure every later module repairs,
then adds the first mechanism: **explicit scope and one item in progress**.

---

## What this module teaches

An agent asked to "add document deletion" is capable of the edit. It still
fails, because nothing around it says what it may touch, what it is working
on, or what comes next. It opens extra work, edits an unrelated file, and
nobody can tell.

Module 1 makes that state explicit in two plain files:

- **`feature_list.json`**: every feature and its status. At most one feature
  may be `in-progress` (WIP=1).
- **`plan.json`**: the paths this work may touch and the one next action.

Then it turns both into checks, because a policy nobody checks is only a
suggestion.

---

## Run in this order

| # | Run | What it shows |
|---|---|---|
| 1 | `python m1_scope_and_state/demos/01_baseline_failure.py` | A capable agent with no harness: what it did, the code it wrote, what it recorded, what is actually true. Score 0 of 5 |
| 2 | `python m1_scope_and_state/demos/02_wip_limit.py` | Why `bool(active)` is not a WIP limit, and why key presence is not a declared scope |
| 3 | `python m1_scope_and_state/demos/03_scope_guard.py` | The same scope rule **enforced before the edit**: a real Claude Code `PreToolUse` hook, on the wire. Also shows what it can't see |
| 4 | [`exercises/ex01_scope_gate.md`](exercises/ex01_scope_gate.md) | **Exercise**: build the scope gate and repair the state files |
| 5 | `python m1_scope_and_state/exercises/check.py` | Rerun until every check passes |

The baseline run is kept under `demos/runs/single-role/`. Its `project/`
folder is a real git repository with the maker's edits in it. Open
`project/kb/kb.py` to see the delete it wrote, and
`project/data/index/documents.json` to see the contradiction for yourself.
Run `git -C m1_scope_and_state/demos/runs/single-role/project status` to see
everything it changed.

---

## Before you start

Record one failure from your own work with agents:

- What did the agent claim?
- What was actually true?
- Which repository mechanism could have exposed the difference?

---

## Opening diagnosis

**Agent = Model + Harness.** The harness is everything except the model, and
it's built from two kinds of control:

| | **Guide**: steers *before* the agent acts | **Sensor**: checks *after* it acts |
| --- | --- | --- |
| **Computational** (deterministic code) | `plan.json` scope, enforced by a hook (M1, M4) | re-executed evidence, tests, lint, `git status`, the done gate (M2, M4) |
| **Inferential** (LLM judgment) | `AGENTS.md`, docs, the handoff (M3) | an LLM reviewer agent: the weakest cell |

The vocabulary comes from Birgitta Böckeler's
[Harness engineering](https://martinfowler.com/articles/harness-engineering.html).
Prefer computational controls wherever the check can be computed.

While the baseline demo's output is on screen, name the control that was
missing behind each failed check:

| Failed check | Missing control | Guide or sensor? | Computational or inferential? |
| --- | --- | --- | --- |
| verification-before-done | | | |
| evidence-true | | | |
| findings-addressed | | | |
| scope-fidelity | | | |
| clean-state | | | |

Modules 1–4 add those controls one at a time. Module 4's ladder reruns this
exact scenario with all of them in place.

---

## Notes for the exercise

Define these in operational terms before you start editing:

- Work item:
- Allowed paths:
- Current feature:
- Next bounded action:
- The check that enforces WIP=1:

After passing, answer: why is "only one in progress" useful even when several
tasks are independent?

---

## Files in this module

| File | What it is |
|---|---|
| `demos/` | Runnable demos; read each file's docstring first |
| `exercises/` | Your working files. Edit them in place; `check.py` checks them |
| `solution/ex01_scope_gate/` | The reference solution |
| `rules.py` | The harness rules this module adds: `validate_features`, `validate_plan`, `scope_violations`. Later modules build on them |
| `hooks/scope_guard.py` | A Claude Code `PreToolUse` hook that blocks any edit outside `plan.json`'s `allowed_paths`, and any edit to `plan.json` itself. A rule written in prose is often ignored; an exit code of 2 is not |
