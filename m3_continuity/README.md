# Module 3 — Continuity (`m3_continuity`)

This module makes a repository **resumable**: a fresh session, with no
transcript, can tell what is true and what to do next.

---

## What this module teaches

Work outlives any single session. Whoever comes next might be a fresh agent,
a parallel agent, a teammate, or you tomorrow, and none of them has the
transcript. If the only record of what was verified, what is still broken,
and what to do next lives in that transcript, the next session has to
rediscover it, or guess. Worse, it may trust a record that is wrong.

A note on current practice: early long-running harnesses wiped the agent's
context on purpose ("context resets") because models wrapped up too early as
their context filled. Newer models largely don't, and those resets became
dead weight. What still matters is the reason they worked: **the state was
written down in files**. That's what this module teaches.

Module 3 moves that state onto disk and checks it before work begins:

- **A router** (`AGENTS.md`) that points to the product, the architecture,
  and the handoff
- **A handoff** (`session-handoff.md`) with three required sections:
  `Verified now`, `Broken or unverified`, `Next best step`
- **A doctor** that runs at startup. It checks the router, the feature state,
  every recorded piece of evidence (Module 2), and the handoff

[`example_repo/`](example_repo/) is a small, healthy repository in exactly
that shape. Read it the way a fresh session would.

---

## Run in this order

| # | Run | What it shows |
|---|---|---|
| 1 | `python m3_continuity/demos/01_doctor.py` | The startup doctor passing on `example_repo/` |
| 2 | `python m3_continuity/demos/02_broken_handoff.py` | Three plausible handoffs judged by the readiness rule; extra sections survive |
| 3 | `python m3_continuity/demos/03_next_session.py` | Session 2 inherits session 1's false record. Without a doctor, its new import *looks* broken because of the old delete bug. With a doctor, it repairs first and import works the first time |
| 4 | [`exercises/ex01_handoff_parser.md`](exercises/ex01_handoff_parser.md) | **Exercise**: parse handoffs, gate readiness, write a next step |
| 5 | `python m3_continuity/exercises/check.py` | Rerun until every check passes |

---

## Notes for the exercise

Your parser must preserve unknown sections. Explain why a harness should be
strict about required sections but tolerant of additional ones:

Write the exact next action a fresh session should take:

---

## Files in this module

| File | What it is |
|---|---|
| `example_repo/` | A healthy, resumable repository: router, docs, feature list, handoff |
| `demos/` | Runnable demos; read each file's docstring first |
| `exercises/` | Your working files. Edit them in place; `check.py` checks them |
| `solution/ex01_handoff_parser/` | The reference solution |
| `rules.py` | The harness rules this module adds: `parse_handoff`, `resume_ready`, `validate_router`, `doctor`. Builds on Module 2's `validate_evidence` |
