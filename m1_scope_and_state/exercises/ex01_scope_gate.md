# Exercise 1 — The scope gate `[Core]`

## Goal

Turn a backlog into executable state, declare what the work may touch, and
enforce one item in progress.

## What's broken

All the files you edit are in this folder:

| File | Defect |
| --- | --- |
| `feature_list.json` | Two features are `in-progress` at once |
| `plan.json` | `allowed_paths` is empty and `next_action` is blank |
| `scope_gate.py` | `assess_scope()` treats any active work as satisfying WIP=1, and treats the *presence* of a key as a declared scope |

## Steps

1. Run the check and read which checks fail:
   ```sh
   python m1_scope_and_state/exercises/check.py
   ```
2. Repair `feature_list.json` so at most one feature is `in-progress`.
3. Complete `plan.json` with the paths the delete work may touch, such as
   `kb/kb.py` and `kb/test_kb.py`, and one bounded next action.
4. Implement `assess_scope()` in `scope_gate.py`:
   - handle zero, one, and several active features
   - reject an empty `allowed_paths` list
   - reject a blank `next_action`
5. Rerun the check until every check passes.

## Verify

- [ ] `scope-function-contract` passes all 4 contract cases
- [ ] `wip-limit` passes on your `feature_list.json`
- [ ] `scope-declared` and `next-action-bounded` pass on your `plan.json`

## Reflection

- Why does `bool(active)` not enforce WIP=1?
- What does a declared scope make measurable later?
- Which file gives a fresh session its next action?

## Stretch `[Optional]`

Implement `scope_violations(allowed_paths, changed_paths)` in the same
`scope_gate.py`:

- An exact path matches itself; an entry ending in `/` covers everything
  beneath that directory.
- `tests/` must not cover `tests_extra/`.
- Treat `\` as `/` and drop a leading `./`.
- Return the violations sorted.

```sh
python m1_scope_and_state/exercises/check.py --stretch
```

This is the comparison a checker needs to enforce declared scope against a
real diff. Module 4's `02_ladder_with_your_code.py` uses your version to score
`scope-fidelity`.

---

> **Solution:** [`solution/ex01_scope_gate/`](../solution/ex01_scope_gate/).
> Check it with `python m1_scope_and_state/exercises/check.py --solution`.
> To start over: `git checkout -- m1_scope_and_state/exercises`.
