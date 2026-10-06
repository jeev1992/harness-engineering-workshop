# Exercise 1 — Reproduce recorded evidence `[Core]`

## Goal

Replace a completion claim with evidence another process can reproduce.

## What's broken

All the files you edit are in this folder:

| File | Defect |
| --- | --- |
| `feature_list.json` | `document-list` is `passing` with the observation `"exit 0: assumed"`, which no command ever produced |
| `evidence.py` | `reproduce()` trusts any non-empty observation and never calls the executor |

## Steps

1. Run the check and read which checks fail:
   ```sh
   python m2_executable_verification/exercises/check.py
   ```
2. Produce a real observation:
   ```sh
   python m2_executable_verification/demos/01_observe.py
   ```
   The command, exit code, and observed output are one unit of evidence.
   Copy the `observed` value into `feature_list.json`.
3. Implement `reproduce()` in `evidence.py`:
   - run the feature's recorded command through the `execute` function you
     are given
   - return the actual exit code and observed output
   - pass only when the exit code is 0 **and** the output exactly matches the
     record
4. Rerun the check until every check passes.

## Verify

- [ ] `evidence-function-contract` passes all 3 contract cases: a valid
      record, fabricated output, and an unsupported command
- [ ] `evidence-reproduces:document-list` passes on your `feature_list.json`

## Reflection

- Why is structured evidence still untrusted until it is re-executed?
- Why must unsupported commands remain explicit failures?
- Where would output normalization belong if exact bytes were too strict?

## Stretch `[Optional]`: a structural lint

Re-executing evidence catches a broken `delete()` *after* it runs. A
structural lint catches it *before* anything runs, by reading the code. This
is the most widely used kind of computational sensor (custom linters and
structural tests). The most useful versions say how to fix what they find,
because the reader is often an agent.

Implement `lint_derived_state(source)` in the same `evidence.py`:

- Report every function that calls `.unlink()` (deletes a source file) but
  never calls `_write_index(...)` (updates the index).
- Start each message with the function's name and `()`, and say how to fix
  it, mentioning `_write_index`.
- Return the messages sorted; return `[]` when the source is clean.

```sh
python m2_executable_verification/exercises/check.py --stretch
```

The check also runs your lint on the real `kb/kb.py`, which must come back
clean. A lint that fires on correct code teaches people, and agents, to
ignore it.

Your `reproduce()` scores the `evidence-true` rubric item when you run Module
4's `02_ladder_with_your_code.py`.

---

> **Solution:** [`solution/ex01_reproduce_evidence/`](../solution/ex01_reproduce_evidence/).
> Check it with `python m2_executable_verification/exercises/check.py --solution`.
> To start over: `git checkout -- m2_executable_verification/exercises`.
