# Exercise 1 — The handoff parser `[Core]`

## Goal

Leave enough honest state for a fresh session to resume without rediscovery.

## What's broken

All the files you edit are in this folder:

| File | Defect |
| --- | --- |
| `session-handoff.md` | Records what passed and what is uncertain, but has no next best step |
| `handoff.py` | `parse_handoff()` drops every section; `resume_ready()` calls any non-empty text ready |

## Steps

1. Run the check and read which checks fail:
   ```sh
   python m3_continuity/exercises/check.py
   ```
2. Implement `parse_handoff()` in `handoff.py`:
   - map each `## Section` heading to its `- ` list items
   - preserve unknown sections and their items
3. Implement `resume_ready()`:
   - the required sections are `Verified now`, `Broken or unverified`, and
     `Next best step`
   - a missing **or empty** required section means not ready
   - report missing sections in that order
4. Add a `## Next best step` to `session-handoff.md`. Make it specific,
   bounded, and consistent with the rest of the handoff.
5. Rerun the check until every check passes.

## Verify

- [ ] `continuity-function-contract` passes all 4 contract cases
- [ ] `handoff-sections` passes on your `session-handoff.md`

## Reflection

- Why preserve sections the checker does not understand?
- What should a startup doctor refuse to tolerate?
- Which facts belong on disk rather than in prompt context?

## Stretch `[Optional]`

Implement `render_handoff(title, sections)` in the same `handoff.py` so your
parser reads its output back unchanged:

- Section order is preserved and empty sections survive.
- The text ends with exactly one newline.
- Rendering a reparsed handoff produces identical text.

```sh
python m3_continuity/exercises/check.py --stretch
```

A harness that writes state must be able to read its own output.

Your `resume_ready()` scores the `clean-state` rubric item when you run Module
4's `02_ladder_with_your_code.py`.

---

> **Solution:** [`solution/ex01_handoff_parser/`](../solution/ex01_handoff_parser/).
> Check it with `python m3_continuity/exercises/check.py --solution`.
> To start over: `git checkout -- m3_continuity/exercises`.
