# Harness Engineering Workshop
## Make agent work bounded, verifiable, resumable, and independently acceptable

A **4-hour hands-on workshop** for engineers who already build agents. It does
not teach orchestration, tool calling, or agent frameworks. Instead, one small
knowledge-base app fails in predictable ways while you build the **execution
system around the agent**: the harness.

Python only. No dependencies, no API keys, no network. The agent's behavior is
scripted and deterministic, and every score is computed by checks that
actually run.

---

## What you'll learn

| Module | Mechanism | Question it answers | How we use it |
|---|---|---|---|
| **M1** | Scope and state | What may change, and what is in progress? | `plan.json` declares scope; `feature_list.json` enforces WIP=1 |
| **M2** | Executable verification | Did the work actually hold? | A feature is `passing` only if its recorded command reproduces |
| **M3** | Continuity | Can a fresh session resume? | A router, an honest handoff, and a startup doctor |
| **M4** | Independent acceptance | Who decides it's done? | Planner, maker, and checker are separate roles; only the checker accepts |

---

## The scenario

**Work item:** *Implement document deletion end to end* in a local
knowledge-base tool ([`kb/kb.py`](kb/kb.py)). Deletion is not built yet.
`python kb/kb.py <data> delete <id>` reports that it is not implemented.

The tool stores source documents **and** a derived metadata index. Deleting a
document correctly means updating both.

| Role | Behavior without a harness |
|---|---|
| **Maker** (the agent) | Writes a `delete()` that removes the file but forgets the index, records evidence it never ran, edits an unrelated file, and declares itself done |
| **Checker** | Absent until Module 4 |
| **Planner** | Absent until Module 4 |

The maker is capable; the system around it is not. Its behavior never changes
during the workshop. Only the harness does. Watching the score go
**0 → 4 → 5** with the same maker is the capstone.

The maker is scripted so the class is repeatable, but its work is real. Each
run gets its own git copy of the project. The maker's code changes are real
edits to that copy, every verification command runs that copy's code as a
separate process, and scope is read from `git status`.

---

## Project structure

Folders are numbered in teaching order. Each module adds one mechanism.

```text
harness-engineering-workshop/
│
├── kb/                                  # THE APP the agent is changing (shared)
│   ├── kb.py                            # init / list / ask / reconcile + command line
│   ├── test_kb.py
│   └── seed/                            # 3 seed documents
│
├── m1_scope_and_state/                  # MODULE 1: bound the work
│   ├── README.md                        # module guide; start here
│   ├── demos/                           # 01 baseline failure, 02 WIP limit, 03 scope guard
│   ├── exercises/                       # ✏️ your files + check.py
│   ├── solution/
│   ├── hooks/                           # the rule enforced inside Claude Code's loop
│   └── rules.py                         # the harness rules this module adds
│
├── m2_executable_verification/          # MODULE 2: claims -> evidence
├── m3_continuity/                       # MODULE 3: resume from the repo alone
│   └── example_repo/                    #   a healthy, resumable repository
├── m4_independent_acceptance/           # MODULE 4: the maker can't accept its own work
│   ├── gate.py                          #   the done gate: every module's rules in one check
│   └── hooks/                           #   a Stop hook that runs the gate before "done"
│                                        #   demos: the 0 -> 4 -> 5 capstone ladder
│
├── shared/                              # scripted maker, rubric, project copies,
│                                        #   check plumbing (read it if curious;
│                                        #   never edit it)
└── instructor/                          # class plan, facilitator script, slides,
                                         #   assessment, full verification, and
                                         #   live/: the Claude Code segment
```

Every module has the same shape: **README → demos → exercise → check**.

---

## Quick start

Needs **Python 3.12 or newer** (tested on 3.12 and 3.14) and Git. There is
nothing to install.

```sh
git clone <this-repo>
cd harness-engineering-workshop
python --version            # 3.12 or newer
git --version
python m3_continuity/demos/01_doctor.py
```

If the last command ends with `Ready to select work.`, you're set. Save the
Module 1 demos for class: the first one is the opening reveal.

On some systems the command is `python3`. With `uv`, use `uv run python ...`.

---

## How each module works

```sh
# 1. Watch the problem
python m2_executable_verification/demos/02_fabricated_evidence.py

# 2. Read the exercise brief
#    m2_executable_verification/exercises/ex01_reproduce_evidence.md

# 3. Edit the files in exercises/, then check
python m2_executable_verification/exercises/check.py

# Optional
python m2_executable_verification/exercises/check.py --stretch    # stretch task
python m2_executable_verification/exercises/check.py --solution   # see the solution pass

# Start over
git checkout -- m2_executable_verification/exercises
```

The first check **must fail**, and it tells you exactly which checks fail and
which files to edit. Edit only the files in that module's `exercises/` folder.

---

## Run reference

One line per runnable file, in teaching order.

### Module 1 — Scope and state

| # | Run | What it means |
|---|---|---|
| 1 | `python m1_scope_and_state/demos/01_baseline_failure.py` | A capable maker with no harness: every claim fails when re-checked. 0 of 5 |
| 2 | `python m1_scope_and_state/demos/02_wip_limit.py` | `bool(active)` is not a WIP limit; key presence is not a declared scope |
| 3 | `python m1_scope_and_state/demos/03_scope_guard.py` | The declared scope enforced *before* an edit: a real Claude Code hook, on the wire |
| 4 | `python m1_scope_and_state/exercises/check.py` | Exercise: the scope gate |

### Module 2 — Executable verification

| # | Run | What it means |
|---|---|---|
| 5 | `python m2_executable_verification/demos/01_observe.py` | Command + exit + observed output = one unit of evidence |
| 6 | `python m2_executable_verification/demos/02_fabricated_evidence.py` | Trusting a record accepts fabrications; re-executing it does not |
| 7 | `python m2_executable_verification/exercises/check.py` | Exercise: reproduce recorded evidence |

`01_observe.py --command` also accepts `"kb test"` and the planner-owned acceptance
checks `"kb delete-roundtrip"` and `"kb import-roundtrip"`, which run the
project's code end to end in a throwaway copy of the data.

### Module 3 — Continuity

| # | Run | What it means |
|---|---|---|
| 8 | `python m3_continuity/demos/01_doctor.py` | A fresh session checks that the repository can explain itself |
| 9 | `python m3_continuity/demos/02_broken_handoff.py` | Plausible handoffs that a fresh session cannot resume from |
| 10 | `python m3_continuity/demos/03_next_session.py` | The next session inherits a false record: without a doctor its new feature *looks* broken; with one it repairs first |
| 11 | `python m3_continuity/exercises/check.py` | Exercise: the handoff parser |

### Module 4 — Independent acceptance

| # | Run | What it means |
|---|---|---|
| 12 | `python m4_independent_acceptance/exercises/check.py` | Exercise: enforce the plan, with a scope guard and its tests |
| 13 | `python m4_independent_acceptance/demos/01_ladder.py` | Same maker, three harnesses: 0 → 4 → 5 |
| 14 | `python m4_independent_acceptance/demos/02_ladder_with_your_code.py` | The ladder scored by *your* exercise code |
| 15 | `python m4_independent_acceptance/demos/03_self_report_vs_diff.py` | *Optional*: scope from the maker's account passes; scope from `git status` fails |
| 16 | `python m4_independent_acceptance/demos/04_stop_gate.py` | "Done" enforced: a real Claude Code Stop hook keeps the agent working until the gate passes |
| 17 | `python m4_independent_acceptance/gate.py <project> [--explain]` | The done gate on any kb project; `--explain` shows why each control exists and when to remove it |

---

## Exercises

| Module | Exercise | You implement | You repair |
|---|---|---|---|
| M1 | [`ex01_scope_gate`](m1_scope_and_state/exercises/ex01_scope_gate.md) | `assess_scope()` | `feature_list.json`, `plan.json` |
| M2 | [`ex01_reproduce_evidence`](m2_executable_verification/exercises/ex01_reproduce_evidence.md) | `reproduce()`; stretch: a structural lint | `feature_list.json` |
| M3 | [`ex01_handoff_parser`](m3_continuity/exercises/ex01_handoff_parser.md) | `parse_handoff()`, `resume_ready()` | `session-handoff.md` |
| M4 | [`ex01_enforce_the_plan`](m4_independent_acceptance/exercises/ex01_enforce_the_plan.md) | `decide()`: the scope guard a Claude Code hook runs | `guard_cases.json`: a two-sided test suite that must catch five broken guards |

Each exercise also has an optional, checked **stretch** task for pairs who
finish early. The capstone ladder reuses four of your functions: two core
(`reproduce`, `resume_ready`) and two stretch (`scope_violations`,
`open_findings`). A check that is too lenient visibly moves a rung.

---

## Workshop schedule (4 hours)

| Time | Segment | Key files |
|---|---|---|
| 0:00–0:25 | Opening failure: diagnose the harness, not the model | `m1…/demos/01_baseline_failure.py` |
| 0:25–0:30 | Live: a real Claude Code run with no harness (instructor) | `instructor/live/` |
| 0:30–1:10 | M1: scope and state | `m1_scope_and_state/` |
| 1:10–1:53 | M2: executable verification | `m2_executable_verification/` |
| 1:53–2:03 | Break | |
| 2:03–2:43 | M3: continuity | `m3_continuity/` |
| 2:43–3:25 | M4: independent acceptance | `m4_independent_acceptance/` |
| 3:25–3:35 | Capstone ladder | `m4…/demos/` |
| 3:35–3:45 | Live: the same agent with the harness (instructor) | `instructor/live/` |
| 3:45–4:00 | Transfer and exit check | [M4 README](m4_independent_acceptance/README.md#transfer-card) |

The timings are a delivery heuristic, not a measured benchmark. Instructor
material, including the minute-by-minute plan and the slide deck, is in
[`instructor/`](instructor/).

---

## Troubleshooting

**`ModuleNotFoundError: No module named 'shared'` (or `kb`, `m1_…`)**
Run commands from the repository root, exactly as written:
`python m1_scope_and_state/demos/01_baseline_failure.py`.

**Errors from inside the workshop's own files before any exercise runs**
The workshop needs Python 3.12 or newer. Check with `python --version`, or try
`python3` or `py -3.12`.

**`git is required` or `FileNotFoundError` mentioning git**
The demos give every run its own git repository. Install Git and make sure
`git --version` works in the same terminal.

**The ladder takes several seconds**
That's expected. Each setup starts real processes and git commands in its
own project copy, so the ladder takes about 5–10 seconds.

**A check passes on the solution but not on my files**
Run `python <module>/exercises/check.py --solution` to see a passing run, then
compare your files with the module's `solution/` folder.

**I want a clean exercise**
`git checkout -- <module>/exercises` restores the starter files.

---

## Attribution

This workshop is a curated derivative of the Harness Engineering curriculum
in `ANI-IN/harness-engineering-session`. It retains the original MIT license.
