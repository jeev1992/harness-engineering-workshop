# Module 4 — Independent acceptance (`m4_independent_acceptance`)

This module separates **planner**, **maker**, and **checker**, so the role
that made a completion claim is never the role that accepts it. It ends with
the capstone ladder.

---

## What this module teaches

Modules 1–3 gave the repository scope, evidence, and continuity. Something
still has to *enforce* them, and the maker cannot do it. A maker that checks
its own work stops when it believes it is done.

| Role | Owns |
|---|---|
| Planner | Declares the work item and allowed scope **before** any edit exists |
| Maker | Edits, runs, and records evidence |
| Checker | Re-executes the rubric, raises findings, and is the only role that accepts |

A checker alone can prove behavior. It cannot tell an intended edit from
scope drift unless a planner declared the scope first. The ladder demo makes
that difference visible.

Two points matter for real systems:

- **The checker should be a script wherever possible.** This module's checker
  is the done gate (`gate.py`): code that re-executes evidence, runs the tests,
  and reads `git status`. An LLM reviewer agent is a weaker sensor. Studies
  reported in late 2026 found that adding one can *lower* success rates, and
  that chains of more than about four handoffs between agents usually fail.
- **Enforce it in the loop, not only afterwards.** `hooks/stop_gate.py` is a
  Claude Code `Stop` hook. When the agent tries to finish, the hook runs the
  gate, and if anything fails, Claude Code keeps the agent working with the
  failures and their fix lines as its next instructions.

---

## Run in this order

| # | Run | What it shows |
|---|---|---|
| 1 | [`exercises/ex01_enforce_the_plan.md`](exercises/ex01_enforce_the_plan.md) | **Exercise**: write the scope guard a Claude Code hook runs before every edit, plus a two-sided test suite that catches five broken guards |
| 2 | `python m4_independent_acceptance/exercises/check.py` | Rerun until every check passes |
| 3 | `python m4_independent_acceptance/demos/01_ladder.py` | **Capstone**: same maker, three harnesses, 0 → 4 → 5 |
| 4 | `python m4_independent_acceptance/demos/02_ladder_with_your_code.py` | The same ladder, scored with the functions *you* wrote in Modules 1–4 |
| 5 | `python m4_independent_acceptance/demos/03_self_report_vs_diff.py` | *Optional*: the same scope rule passes the maker's own account and fails `git status` |
| 6 | `python m4_independent_acceptance/demos/04_stop_gate.py` | "Done" enforced: a real Claude Code `Stop` hook refuses the baseline's "delete works" and releases the finished run |
| 7 | `python m4_independent_acceptance/gate.py --explain` | Why each control exists, and when it should be removed |

---

## Notes for the exercise

The planner's scope only matters if something enforces it. In the exercise
you write that enforcement: the decision a `PreToolUse` hook makes before every
edit. Then you prove it's right **in both directions**. A guard whose tests only
list what to block can quietly drift into blocking everything, so the check
runs your tests against five deliberately broken guards (mutation testing).

For the delete work item, assign responsibility:

| Decision | Planner | Maker | Checker |
| --- | --- | --- | --- |
| Declare allowed scope | | | |
| Edit implementation | | | |
| Execute verification | | | |
| Accept completion | | | |

Explain why a checker without a prior plan cannot detect scope drift:

---

## Capstone: the ladder

Run `01_ladder.py`. Do not read the scores first. Compare the FAIL lines:

- What does `gen-eval` repair?
- What remains invisible?
- What new artifact lets `plan-gen-eval` detect it?

Every run is a real git repository under `demos/runs/<setup>/project/`. Open
`gen-eval/project/config/retrieval-notes.md` to see the out-of-scope edit
that shipped. Then open the `plan-gen-eval` transcript to see who found it
and who reverted it. Scope is measured with `git status` in each project,
never from the maker's transcript. Demo 03 shows why that matters.

Then run `02_ladder_with_your_code.py`:

- Did your functions reproduce `0 -> 4 -> 5`?
- Does any of them fail its own exercise check? Why didn't the ladder notice?

Then run `04_stop_gate.py`. The baseline's own tests **pass**, because it
wrote no delete test, yet the gate still refuses it: the re-executed evidence
exits 1. Read each fix line as the agent would.

Finally, `gate.py --explain`. Every control records why it exists. **Contract**
controls define done and never expire. **Compensating** controls work around
something a model gets wrong today. Remove them when that stops being true,
and prove it with an eval first. Harnesses rot when nobody does this.

---

## Transfer card

Choose one real repository you own and complete:

- Failure to prevent:
- Durable input artifact:
- Executed command:
- Passing observation:
- Failing observation:
- Role allowed to accept:
- Where the check will run:

## Exit check

Answer without notes:

1. What is the difference between a completion claim and evidence?
2. What state must survive the end of a session, for whoever comes next?
3. What can a planner make visible that a checker alone cannot?

---

## Files in this module

| File | What it is |
|---|---|
| `demos/` | The capstone ladder (reference rubric and your code), self-report versus diff, and the stop gate on the wire |
| `exercises/` | Your working files. Edit them in place; `check.py` checks them |
| `solution/ex01_enforce_the_plan/` | The reference solution |
| `rules.py` | The findings rule the checker uses: `open_findings` |
| `gate.py` | The done gate: Modules 1–4's rules in one check over a project, with a fix line per failure and `--explain` |
| `hooks/stop_gate.py` | A Claude Code `Stop` hook that runs the gate and keeps the agent working until it passes |

The scripted maker and the five-check rubric the ladder runs live in
[`shared/scenario.py`](../shared/scenario.py).
