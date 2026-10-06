# Module 2 — Executable verification (`m2_executable_verification`)

This module replaces **completion claims** with **evidence another process can
reproduce**.

---

## What this module teaches

In the baseline, the agent marked deletion `passing` and recorded
`"exit 0: assumed"`. That is a claim, not an observation. No command ever
produced it.

Evidence is three things recorded together:

```text
command + exit code + observed output
```

Recording them is not enough either. Evidence becomes trustworthy only when a
different process **re-executes** the command and gets the same result now.

Module 2 adds that rule on top of Module 1's feature list: a feature may be
`passing` only if its recorded evidence reproduces.

---

## Run in this order

| # | Run | What it shows |
|---|---|---|
| 1 | `python m2_executable_verification/demos/01_observe.py` | One real unit of evidence: command, exit, observed output |
| 2 | `python m2_executable_verification/demos/02_fabricated_evidence.py` | Trusting a record versus re-executing it, across real, assumed, and unsupported evidence |
| 3 | [`exercises/ex01_reproduce_evidence.md`](exercises/ex01_reproduce_evidence.md) | **Exercise**: implement `reproduce()` and replace the assumed observation |
| 4 | `python m2_executable_verification/exercises/check.py` | Rerun until every check passes |

`01_observe.py` also accepts `--command "kb ask deletion"` and
`--command "kb test"`. Those three are the only verification commands the
workshop supports. Each one runs as a **separate process** inside a copy of
the project, and the output shows the real command line in `"process"`. Any
other command exits 2 as an explicit failure.

---

## Notes for the exercise

Record the real observation you generated:

- Command:
- Exit:
- Observed:
- Why a timestamp alone would not make this evidence:
- Why review is weaker than re-execution for this check:

---

## Files in this module

| File | What it is |
|---|---|
| `demos/` | Runnable demos; read each file's docstring first |
| `exercises/` | Your working files. Edit them in place; `check.py` checks them |
| `solution/ex01_reproduce_evidence/` | The reference solution |
| `rules.py` | The harness rules this module adds: `execute`, `reproduce`, `validate_evidence`. Builds on Module 1's `validate_features` |
