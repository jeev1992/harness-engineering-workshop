# Exercise 1 — Enforce the plan: a scope guard and its tests `[Core]`

## Goal

The planner declared what this work may touch. Make that boundary
**enforced**, not just written down, and prove that your enforcement is right
in both directions.

A rule written in prose ("only touch `kb/kb.py`") is often ignored. A Claude
Code `PreToolUse` hook isn't: Claude Code runs it before every edit, and when
it exits 2 the edit doesn't happen. You'll write that hook's decision.

## What's broken

All the files you edit are in this folder:

| File | Defect |
| --- | --- |
| `guard.py` | `decide()` takes a tempting shortcut: `path.endswith(entry)`. It blocks harmless tools, blocks the work-tracking files, and can be fooled by paths that merely end the right way |
| `guard_cases.json` | Your test suite only lists what the guard must **block**. A guard that blocks everything passes it |

## Steps

1. Run the check and read which checks fail:
   ```sh
   python m4_independent_acceptance/exercises/check.py
   ```
2. Implement `decide(event, project, plan)` in `guard.py`, following the seven
   rules in its docstring. `event` is the JSON Claude Code sends,
   `project` is the absolute project root, and `plan` is `plan.json` (or
   `None`). Return `(ALLOW, "")` or `(BLOCK, "Blocked: ...")`.
3. Grow `guard_cases.json` into a **two-sided** suite. Each case looks like:
   ```json
   {"label": "the planned code", "tool": "Edit", "path": "kb/kb.py", "expect": "allow"}
   {"label": "a shell command", "tool": "Bash", "command": "python -m unittest", "expect": "allow"}
   {"label": "before any plan", "tool": "Edit", "path": "kb/kb.py", "plan": null, "expect": "block"}
   ```
   Paths are relative to the project. The plan is
   `{"allowed_paths": ["kb/kb.py", "kb/test_kb.py", "docs/"]}` unless a case
   says otherwise.
4. Rerun the check until every check passes.

## Verify

- [ ] `guard-function-contract`: your guard decides all 13 hidden cases correctly
- [ ] `cases-both-directions`: at least 3 must-block **and** 3 must-allow cases
- [ ] `cases-agree-with-reference`: every expectation in your suite is right
- [ ] `cases-catch-mutants`: each of the five broken guards fails at least one
      of your cases. The broken guards are: allows everything, blocks everything,
      blocks tools that don't edit, no exemption for state files, matches paths by
      prefix

The last check is **mutation testing**, applied to your harness's tests. A
suite that no broken guard can fail isn't testing anything.

## Reflection

- Why must a guard's tests include what it must *allow*? What happens to a
  harness whose tests only check what it blocks?
- Your guard never sees `echo x > notes.md` run through the shell. What
  catches that edit? (Hint: `python m4_independent_acceptance/gate.py --explain`.)
- What can a checker prove without a plan, and what can a guard enforce?

## Stretch `[Optional]`

Implement `open_findings(events)` in the same `guard.py`. It is the
`findings-addressed` rule the capstone ladder uses. A finding is closed only by
a later fix with the same id, followed by a passing verification after that
fix.

```sh
python m4_independent_acceptance/exercises/check.py --stretch
```

The contract cases include a fix that predates its finding and a verification
that predates its fix. Module 4's `02_ladder_with_your_code.py` uses your
version to score `findings-addressed`.

---

> **Solution:** [`solution/ex01_enforce_the_plan/`](../solution/ex01_enforce_the_plan/).
> Check it with `python m4_independent_acceptance/exercises/check.py --solution`.
> The real hook, which reads `plan.json` from disk, is
> [`m1_scope_and_state/hooks/scope_guard.py`](../../m1_scope_and_state/hooks/scope_guard.py).
> To start over: `git checkout -- m4_independent_acceptance/exercises`.
