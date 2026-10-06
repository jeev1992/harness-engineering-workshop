# Instructor guide

Everything in this folder is for the person delivering the class. Students
work only in the root `README.md` and the four `m*` module folders.

| File | Purpose |
| --- | --- |
| [class-plan.md](class-plan.md) | The 240-minute delivery contract |
| [facilitator-script.md](facilitator-script.md) | Exact flow, prompts, commands, hints, debriefs, and transitions |
| [slides.md](slides.md) | Marp-compatible deck. Slides before the `Appendix` divider form the timed 240-minute path, each with a `Clock HH:MM \| N min` presenter note. Appendix slides are untimed deep dives and post-exercise reference |
| [assessment.md](assessment.md) | Formative checks, exit prompts, and answer guide |
| [verify_all.py](verify_all.py) | Full verification: doctor, unit tests, every starter and solution, lint |
| [lint.py](lint.py) | Trailing whitespace, Python and JSON syntax, local Markdown links |
| [tests/](tests/) | Workshop-level tests, including the slide clock, the 0 → 4 → 5 ladder, two-sided hook tests, and the live tooling |
| [live/RUNBOOK.md](live/RUNBOOK.md) | The live Claude Code segment: setup, rehearsal, fallback, and what to say |
| [live/setup_project.py](live/setup_project.py) | Builds a bare or harnessed kb project *outside* the workshop for Claude Code, with optional one-control ablation |
| [live/score_project.py](live/score_project.py) | Scores live runs: a hidden eval (did it work?) and the done gate (could the repository prove it?) |

The learner-facing notes that used to live in a separate workbook are now in
the module READMEs. The opening diagnosis is in Module 1. The transfer card
and exit check are in Module 4.

## Before class

From a fresh clone (Git must be installed: every scripted run is its own git
repository):

```sh
python instructor/verify_all.py
python m1_scope_and_state/demos/01_baseline_failure.py
python m4_independent_acceptance/demos/01_ladder.py
```

`verify_all.py` checks each module's `exercises/` folder against the exact
checks its starter must fail (`STARTER_FAILS_WITH` in each `check.py`). Run it
on a clean checkout, not on a copy where the exercises have been solved. It
takes about a minute, because the tests start real processes and git
repositories.

The day before, also rehearse the live segment and record a fallback:
[live/RUNBOOK.md](live/RUNBOOK.md).

Solutions sit next to the exercises in each module's `solution/` folder.
Ask pairs to state the failed check before they open one.

## Resetting a student's exercise

```sh
git checkout -- m3_continuity/exercises
```

The facilitator script uses this to demonstrate a lenient check moving a
ladder rung: reset the Module 3 exercise to its starter, then run
`02_ladder_with_your_code.py`. The ladder moves to `1 -> 4 -> 5`.
