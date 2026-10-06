---
marp: true
theme: default
paginate: true
header: "Harness Engineering"
footer: "Build the execution system around the agent"
style: |
  section {
    font-family: "Aptos", "Segoe UI", sans-serif;
    color: #172033;
    background: #f7f9fc;
    padding: 56px 68px;
  }
  section.lead {
    color: #ffffff;
    background: linear-gradient(135deg, #172033 0%, #243b67 100%);
  }
  section.section {
    color: #ffffff;
    background: #243b67;
  }
  h1, h2 {
    color: #173f7a;
  }
  section.lead h1, section.lead h2,
  section.section h1, section.section h2 {
    color: #ffffff;
  }
  code {
    background: #e9eef7;
  }
  table {
    font-size: 0.78em;
  }
  blockquote {
    border-left: 6px solid #2f6fed;
    color: #243b67;
  }
---

<!-- _class: lead -->
<!-- _header: "" -->
<!-- _footer: "" -->

# Harness Engineering

## Build the execution system around the agent

Complete four-hour engineering class

<!--
Open with the distinction that matters: the agent's capability is held
constant today. We change the execution system around it.
-->

<!-- Clock 00:00 | 1 min -->

---

# The class contract

Today, the agent does **not** get smarter.

We hold maker behavior constant and change:

- What the maker can know
- What it may change
- What state survives
- What establishes completion
- Who is allowed to accept the claim

<!--
Ask participants not to solve failures by proposing a larger model or a longer
prompt. Every intervention must be a repository mechanism or executable check.
-->

<!-- Clock 00:01 | 2 min -->

---

# What you will leave able to build

By the end of this class, you can:

- Diagnose failures as a missing guide or sensor
- Bound work with executable scope and WIP limits
- Replace completion claims with reproducible evidence
- Make repository state resumable across sessions
- Separate making from independent acceptance
- Add one concrete harness predicate to your own repository

<!--
Read these as engineering outcomes, not learning-topic
headings. Tell participants each outcome will be demonstrated by a command.
-->

<!-- Clock 00:03 | 1 min -->

---

# One work item for the entire class

> Implement document deletion end to end in a local knowledge-base tool.

The maker:

1. Deletes the visible document
2. Forgets derived state
3. Records assumed evidence
4. Edits an unrelated retrieval file
5. Declares completion

<!--
Deletion is intentionally ordinary. It is small enough to invite trust and
stateful enough to expose why that trust is unsafe.
-->

<!-- Clock 00:04 | 2 min -->

---

# The knowledge-base system

```text
documents/
  source files
      ↓ init / import / delete
index/documents.json
  metadata system of record
      ↓ ask
grounded answer + citations
```

Deletion is correct only when source and derived state agree.

<!--
Walk from source document to index to answer. Emphasize
that deleting only the visible file creates a state-consistency failure.
-->

<!-- Clock 00:06 | 1 min -->

---

# What would make the claim true?

Before we run anything:

- What state must deletion update?
- What command would establish that?
- What would a new session need to know?
- Which edits are actually in scope?
- Should the maker accept its own work?

<!--
Take answers from the room. Do not resolve them yet. These become the five
predicate families shown after the demo.
-->

<!-- Clock 00:07 | 3 min -->

---

<!-- _class: section -->

# Opening failure

## Diagnose the harness, not the model

<!-- Clock 00:10 | 0 min -->

---

# Run the unchecked baseline

```sh
python m1_scope_and_state/demos/01_baseline_failure.py
```

It prints, side by side:

1. What the maker **did** (its transcript)
2. What the maker **wrote** (its real `delete()`)
3. What the maker **recorded** (its feature list)
4. What is **actually true** (commands re-executed now, and `git status`)

The non-zero exit is expected.

<!--
Switch to the terminal and run it. Point at two lines before anything else:
documents/ has 2 files, but kb list still indexes 3. The maker's claim says
"listing unaffected". Then point at its delete(): there is no index update.
Ask participants to classify each rubric failure.
The run is a real git project under m1_scope_and_state/demos/runs/single-role/project/.
-->

<!-- Clock 00:10 | 3 min -->

---

# Failure 1 — Verification happened too late

```text
maker  edit    kb/kb.py
maker  action  kb delete team-meeting
maker  edit    config/retrieval-notes.md
maker  claim   delete works; listing unaffected
maker  done
```

Missing before `done`:

```text
checker: verification(command, exit, observed)
```

The order of events is part of the predicate.

<!--
A test run after shipping does not justify the earlier
completion event. Verification must precede acceptance.
-->

<!-- Clock 00:13 | 2 min -->

---

# Failure 2 — Evidence was fabricated

Recorded:

```json
{
  "command": "kb ask deletion",
  "observed": "exit 0: assumed"
}
```

The command looks plausible.

The observation was never produced by execution. Re-executed now:

```text
kb ask deletion  exit 1  error: indexed document team-meeting
                         has no source file team-meeting.txt
```

<!--
Structured JSON often creates false confidence. Ask how
the system can distinguish recorded execution from plausible text.
-->

<!-- Clock 00:15 | 2 min -->

---

# Failure 3 — Findings had no lifecycle

A useful finding needs:

```text
finding
   ↓ assigned repair
fix
   ↓ same predicate rerun
passing verification
```

A list of findings is state.

A closed verification loop is progress.

<!--
Connect this to issue trackers that mark work done without
rerunning the condition that opened the issue.
-->

<!-- Clock 00:17 | 1 min -->

---

# Failure 4 — Scope drift was invisible

The maker edited:

```text
kb/kb.py
config/retrieval-notes.md
```

Which edit is unrelated?

Without a declared scope, the checker has no mechanical answer.

<!--
Let the room answer by intuition, then point out that the
system cannot encode that intuition without a prior declaration.
-->

<!-- Clock 00:18 | 2 min -->

---

# Failure 5 — Final state was not resumable

At session end:

- Feature status claimed `passing`
- Evidence did not reproduce
- Handoff omitted the next action
- Derived state was inconsistent: the index still lists `team-meeting`,
  whose file is gone

The next session inherits uncertainty, not progress.

<!--
Clean state does not mean no unfinished work. It means
unfinished work is represented honestly and can be resumed.
-->

<!-- Clock 00:20 | 2 min -->

---

# Agent = Model + Harness

The harness is everything except the model. It has two kinds of control:

| | **Guide**: before the agent acts | **Sensor**: after it acts |
| --- | --- | --- |
| **Computational** (code) | `plan.json` scope, enforced by the scope-guard hook | re-executed evidence · tests · lint · `git status` · the done gate |
| **Inferential** (LLM) | `AGENTS.md`, docs, the handoff | an LLM reviewer agent |

Prefer computational controls wherever the check can be computed.

<!--
Vocabulary from Birgitta Böckeler (martinfowler.com, "Harness engineering").
Map the class: M1 and M4 build guides, M2 and M4 build sensors, M3 makes the
handoff and doctor. Ask the room to classify each baseline failure: which
control was missing, a guide or a sensor? Computational or inferential?
Reported studies found LLM reviewer agents can lower success rates; that's why
the bottom-right cell is the weakest.
-->

<!-- Clock 00:22 | 2 min -->

---

# Orchestration and harnesses answer different questions

| Orchestration | Harness |
| --- | --- |
| What happens next? | What is true now? |
| Which role receives work? | What may that role change? |
| Which tool is called? | What output establishes success? |
| How does the flow continue? | What state survives interruption? |

Harness engineering does not replace orchestration.

It makes orchestration operate over inspectable truth.

<!-- Clock 00:24 | 1 min -->

---

# Live: a real agent, no harness

The same task, given to real Claude Code at the start of class:

```sh
python instructor/live/score_project.py ../live-off
```

- **Hidden eval**: did delete actually work? (cases the agent never saw)
- **Done gate**: could the repository prove it?

<!--
Instructor-run; see instructor/live/RUNBOOK.md. Read the hidden eval first. If the bare
run passed it, say so: the harness's value here will be proof, not rescue. If it failed,
name the cause before moving on (usually the index, as in the scripted baseline).
-->

<!-- Clock 00:25 | 5 min -->

---

<!-- _class: section -->

# Mechanism 1

## Scope and executable state

<!-- Clock 00:30 | 0 min -->

---

# The convergence loop

```text
read durable state
      ↓
select one bounded action
      ↓
make change
      ↓
execute predicate
      ↓
record observation
      ↓
repair or advance
```

The loop advances only on evidence.

<!--
This is the backbone for the remaining class. Each lab
implements one boundary in this loop.
-->

<!-- Clock 00:30 | 2 min -->

---

# A backlog is not executable state

```text
Backlog item
    ↓ selected
In-progress feature
    ↓ verified
Passing feature + evidence
```

A useful state artifact answers:

- What owns the next action?
- What is blocked?
- What has executable evidence?
- What has not started?

<!-- Clock 00:32 | 2 min -->

---

# Feature state is a machine contract

Allowed statuses:

```text
not-started
in-progress
blocked
passing
```

Not allowed:

```text
mostly-done
looks-good
probably-passing
```

<!--
Status names should represent transitions the harness can
validate. Subjective progress language cannot drive a gate.
-->

<!-- Clock 00:34 | 2 min -->

---

# State transition rules

```text
not-started ──select──▶ in-progress
in-progress ──dependency──▶ blocked
blocked ──dependency cleared──▶ in-progress
in-progress ──verification passes──▶ passing
passing ──evidence stops reproducing──▶ in-progress
```

Regression is a valid transition.

<!--
The last transition matters: passing is not permanent when
the evidence no longer reproduces.
-->

<!-- Clock 00:36 | 2 min -->

---

# Why WIP=1 here?

WIP=1 is a **harness policy for this work unit**.

It prevents one session from:

- Opening multiple partial changes
- Leaving ambiguous ownership
- Recording incompatible next actions
- Ending with several unsettled states

It is not a universal claim about team process.

<!-- Clock 00:38 | 2 min -->

---

# The broken WIP predicate

```python
active = [
    feature
    for feature in features
    if feature["status"] == "in-progress"
]

return bool(active)  # Wrong
```

This proves “some work is active.”

It does not prove “at most one item is active.”

<!--
Ask participants for the correct bound, but do not confirm it: M1 exercise
checks it, and the answer slide is in the appendix.
-->

<!-- Clock 00:40 | 2 min -->

---

# Declared scope creates a comparison boundary

```json
{
  "work_item": "Implement document deletion end to end",
  "allowed_paths": [
    "kb/kb.py",
    "kb/test_kb.py"
  ],
  "next_action": "Add the failing deletion test"
}
```

Without declared intent, an unrelated edit is merely another edit.

<!-- Clock 00:42 | 2 min -->

---

# Scope needs two observations

```text
Plan artifact:
  allowed_paths

Repository observation:
  actual changed paths

Predicate:
  actual_paths ⊆ allowed_paths
```

The plan alone does not enforce scope.

The diff alone does not explain intent.

<!--
Both halves are required. This becomes the core insight in
Module 4 when the planner is introduced.
-->

<!-- Clock 00:44 | 1 min -->

---

# M1 exercise — Scope and state

```sh
python m1_scope_and_state/exercises/check.py
```

Implement and repair:

1. WIP=1 over zero, one, and multiple active features
2. Non-empty allowed scope
3. A bounded next action
4. `assess_scope(...)`

<!--
Run the first `check.py` live so the room sees the starter fail.
Pairs read the failed predicates before editing anything.
-->

<!-- Clock 00:45 | 3 min -->

---

# M1 exercise — Work time: contract cases

`check.py` runs these against your `assess_scope`:

| # | Input | Expected |
| --- | --- | --- |
| 1 | No feature in progress | WIP passes |
| 2 | One feature in progress | WIP passes |
| 3 | Two features in progress | WIP fails |
| 4 | Empty `allowed_paths`, blank `next_action` | Scope and next action fail |

It also checks your repaired `feature_list.json` and `plan.json`.

A failure names the case: `failing case(s) 1, 3 of 4`.

<!--
Leave this slide up while pairs work. At minute 10 of work time, hint that
key presence is not the same as a non-empty value.
-->

<!-- Clock 00:48 | 12 min -->

---

# M1 exercise — Stretch: scope against a real diff

Finished the core? Implement `scope_violations(allowed_paths, changed_paths)`:

- Exact paths match; `dir/` entries cover everything beneath them
- `tests/` must **not** cover `tests_extra/`
- Treat `\` as `/` and drop a leading `./`
- Return violations sorted

```sh
python m1_scope_and_state/exercises/check.py --stretch
```

In the capstone, yours scores `scope-fidelity`.

<!--
Pairs still on the core keep working on the core. Do not pull the room
forward; the stretch exists so fast pairs are not idle.
-->

<!-- Clock 01:00 | 5 min -->

---

# M1 exercise debrief

- Why does `bool(active)` fail as a WIP limit?
- Which artifact survives a fresh session?
- What does declared scope make measurable later?
- How would you compare allowed paths with the real Git diff?

> A plan is useful when it creates a predicate, not when it creates prose.

<!-- Clock 01:05 | 5 min -->

---

<!-- _class: section -->

# Mechanism 2

## Executable verification

<!-- Clock 01:10 | 0 min -->

---

# Claim, record, observation

```text
Claim:
  "Document listing works."

Record:
  command = "kb list"
  observed = "exit 0: assumed"

Observation:
  execute command now
  capture actual exit and output
```

Structure alone does not make evidence trustworthy.

<!-- Clock 01:10 | 2 min -->

---

# The evidence tuple

```text
command + exit + observed output
```

Evidence becomes useful when another process can:

1. Execute the same command
2. Observe the current result
3. Compare it with the record
4. Reject divergence

<!-- Clock 01:12 | 2 min -->

---

# Evidence has a lifecycle

```text
execute
  ↓
capture exit + output
  ↓
record against feature
  ↓
re-execute independently
  ↓
compare
  ↓
accept or invalidate status
```

Recording is only the middle of the lifecycle.

<!--
Many systems stop after capture. Independent reproduction
is what turns the record into a checkable claim.
-->

<!-- Clock 01:14 | 2 min -->

---

# Unsupported commands are explicit failures

```text
command: unsupported
exit: 2
observed: unsupported verification command
```

Do not:

- Treat unknown commands as skipped
- Convert them to success
- Silently choose a similar command

The verification surface is part of the contract.

<!--
Silent fallback creates success-shaped output and makes
misspelled or obsolete evidence appear valid.
-->

<!-- Clock 01:16 | 2 min -->

---

# Re-execution beats review

Review asks:

> Does this change look correct?

Re-execution asks:

> Does the repository currently satisfy this predicate?

Use review for properties that require judgment.

Use execution whenever the property can be made mechanical.

<!-- Clock 01:18 | 2 min -->

---

# Normalization must be declared

Exact comparison may need normalization for:

- Line endings
- Path separators
- JSON key order
- Trailing whitespace
- Stable timestamps or IDs

Normalize known representation differences.

Do not normalize semantic disagreement away.

<!--
Use JSON key order as the benign example and a missing
document as the semantic difference that must remain visible.
-->

<!-- Clock 01:20 | 2 min -->

---

# Generate a real observation

```sh
python m2_executable_verification/demos/01_observe.py
```

The command returns:

```json
{
  "command": "kb list",
  "exit": 0,
  "observed": "{...actual canonical output...}"
}
```

<!--
Run the command live. Point out that the observed field is produced by the
system rather than typed into the feature record.
-->

<!-- Clock 01:22 | 3 min -->

---

# M2 exercise — Executable verification

```sh
python m2_executable_verification/exercises/check.py
python m2_executable_verification/demos/01_observe.py
```

Implement `reproduce(...)` so it:

- Calls the injected executor
- Preserves actual exit and output
- Requires exit zero
- Requires exact output reproduction
- Fails explicitly for unsupported commands

<!--
Ask why dependency injection is useful here: the exercise
tests verification policy without invoking a shell.
-->

<!-- Clock 01:25 | 3 min -->

---

# M2 exercise — Work time: contract cases

`check.py` runs your `reproduce` with a real executor:

| # | Recorded evidence | Expected report |
| --- | --- | --- |
| 1 | `kb list` with its real output | `passed: true`, exit 0 |
| 2 | `kb list` with `exit 0: assumed` | `passed: false`, actual output |
| 3 | An unsupported command | `passed: false`, exit 2 |

Then replace the assumed observation in your `feature_list.json`:

```sh
python m2_executable_verification/demos/01_observe.py
```

Your `reproduce` scores `evidence-true` in the capstone.

<!--
Leave this slide up while pairs work. If a pair is stuck, ask what their
function returns as `observed` and where that value came from.
-->

<!-- Clock 01:28 | 15 min -->

---

# M2 exercise — Stretch: a structural lint

Evidence catches a broken `delete()` after it runs. A lint catches it **before**:

```text
delete() deletes a source file but never updates the index.
Fix: call _write_index(...) in delete() after removing the file; ...
```

Implement `lint_derived_state(source)`: flag every function that calls
`.unlink()` but never `_write_index(...)`, with a fix in every message.

```sh
python m2_executable_verification/exercises/check.py --stretch
```

A computational sensor that reads code, and talks to the agent.

<!--
Custom linters and structural tests are the most mature sensors teams adopt.
The check also runs the lint on the real kb/kb.py, which must come back clean:
a lint that fires on correct code teaches everyone to ignore it.
-->

<!-- Clock 01:43 | 5 min -->

---

# M2 exercise debrief

- Which fields are assertions?
- Which fields are observations?
- Why is fabricated structured evidence still fabricated?
- When would exact bytes be too strict?
- Where should normalization live?

> A `passing` label is a cached claim.
> The command is the authority.

<!-- Clock 01:48 | 5 min -->

---

<!-- _class: section -->

# Break

## 10 minutes

Leave the successful M2 exercise output visible.

<!-- Clock 01:53 | 10 min -->

---

<!-- _class: section -->

# Mechanism 3

## Continuity and repository readability

<!-- Clock 02:03 | 0 min -->

---

# Context ends

What can a new session know if the transcript is gone?

Not:

- What the previous session intended
- Which checks actually ran
- What remains broken
- Which action should happen next

Unless that state exists in the repository.

<!-- Clock 02:03 | 2 min -->

---

# The repository becomes the system of record

```text
Transcript
  useful history, temporary context

Repository artifacts
  current scope, state, evidence, handoff

Commands
  current observable truth
```

The next session trusts artifacts and re-execution, not memory.

<!--
This does not mean storing every thought. Store the minimum
state required to continue and verify work.
-->

<!-- Clock 02:05 | 2 min -->

---

# Router versus encyclopedia

`AGENTS.md` should answer:

```text
Where do I read product behavior?
Where do I read architecture?
What state do I inspect first?
What command proves readiness?
```

It should route to focused sources instead of duplicating all of them.

<!--
Duplication creates drift. A router remains short enough
for every session to read and points to authoritative detail on demand.
-->

<!-- Clock 02:07 | 2 min -->

---

# Startup is its own phase

```text
resume handoff
      ↓
doctor environment and state
      ↓
select current feature
      ↓
confirm allowed scope
      ↓
begin making
```

Do not discover a broken workspace after editing begins.

<!--
Compare this with a human engineer pulling latest changes
and checking the build before starting a feature.
-->

<!-- Clock 02:09 | 2 min -->

---

# Minimum honest handoff

```md
## Verified now

- Facts established by commands

## Broken or unverified

- Known uncertainty and failures

## Next best step

- One bounded action
```

The handoff is state, not a narrative summary.

<!-- Clock 02:11 | 2 min -->

---

# Weak and strong handoffs

| Weak | Strong |
| --- | --- |
| “Delete is mostly done” | Names the command that passed |
| “Some tests still fail” | Names broken predicate |
| “Continue tomorrow” | Names one bounded next action |
| Repeats transcript | Records current truth |

A handoff should reduce rediscovery.

<!--
Ask participants to rewrite one weak example aloud.
-->

<!-- Clock 02:13 | 3 min -->

---

# Strict requirements, tolerant extensions

The reader must:

- Require the three readiness sections
- Reject missing or empty required sections
- Preserve unknown additive sections
- Report missing sections deterministically

Strict about truth.

Tolerant about extension.

<!-- Clock 02:16 | 2 min -->

---

# M3 exercise — Continuity

```sh
python m3_continuity/exercises/check.py
```

Implement:

1. `parse_handoff(...)`
2. Unknown-section preservation
3. `resume_ready(...)`
4. Ordered missing-section reporting
5. A bounded next action in the handoff

<!--
Pairs who pass the core move to the round-trip stretch; the checker
covers it with `--stretch`.
-->

<!-- Clock 02:18 | 3 min -->

---

# M3 exercise — Work time: contract cases

`check.py` runs these against your parser:

| # | Input | Expected |
| --- | --- | --- |
| 1 | Handoff with an extra `Notes` section | All sections parsed, `Notes` kept |
| 2 | All required sections present | `ready: true` |
| 3 | Only `Verified now` | Missing list in required order |
| 4 | `Broken or unverified` heading, no items | Not ready |

Then add a bounded `Next best step` to your `session-handoff.md`.

Your `resume_ready` scores `clean-state` in the capstone.

<!--
Leave this slide up while pairs work. Case 4 catches parsers that check for
the heading but not its content.
-->

<!-- Clock 02:21 | 12 min -->

---

# M3 exercise — Stretch: round-trip the handoff

Implement `render_handoff(title, sections)` so that:

```python
parse_handoff(render_handoff(title, sections)) == sections
```

- Section order preserved
- Empty sections survive
- Exactly one trailing newline
- Re-rendering a reparsed handoff changes nothing

```sh
python m3_continuity/exercises/check.py --stretch
```

<!--
A harness that writes state must be able to read its own output. This is
the property that lets tooling rewrite a handoff without losing sections.
-->

<!-- Clock 02:33 | 5 min -->

---

# M3 exercise debrief

- Why is “everything is fine” a bad handoff?
- What should the startup doctor refuse to tolerate?
- What belongs on disk rather than in prompt context?
- Why preserve sections the checker does not know?

> The next session should resume, not rediscover.

<!-- Clock 02:38 | 5 min -->

---

<!-- _class: section -->

# Mechanism 4

## Independent acceptance

<!-- Clock 02:43 | 0 min -->

---

# Three logical responsibilities

```text
Planner
  declares intent and allowed scope
        ↓
Maker
  changes the repository
        ↓
Checker
  executes predicates and accepts or rejects
```

Logical separation does not always require three models.

It does require distinct decisions.

<!-- Clock 02:43 | 2 min -->

---

# What can gen-eval prove?

A checker can:

- Re-run feature verification
- Reproduce evidence
- Detect unresolved findings
- Check clean final state

But without a prior plan:

> How does it know an unrelated edit was unrelated?

<!-- Clock 02:45 | 2 min -->

---

# The planner creates the missing boundary

```text
Declared allowed scope
        +
Observed edit set
        ↓
Scope-fidelity predicate
```

No declaration → no comparison boundary.

No comparison boundary → scope drift remains invisible.

<!-- Clock 02:47 | 2 min -->

---

# Plan-gen-eval flow

```text
planner declares scope
          ↓
maker edits
          ↓
checker executes predicates
          +
checker diffs edits against plan
          ↓
repair and recheck
```

Planning adds a new observable, not just another role.

<!--
The additional role matters because it creates `plan.json`
before generation, enabling the scope-fidelity predicate.
-->

<!-- Clock 02:49 | 2 min -->

---

# Rubrics must be executable

Weak rubric item:

```text
The solution is high quality.
```

Executable rubric item:

```text
Every changed path is inside plan.allowed_scope.
```

If a predicate requires judgment, name the evidence and the responsible role.

<!--
Not every valuable property is fully automatable. The
rubric must still state what evidence a reviewer uses.
-->

<!-- Clock 02:51 | 2 min -->

---

# Findings need identity

```json
{
  "type": "finding",
  "id": "out-of-scope:config/retrieval-notes.md",
  "target": "config/retrieval-notes.md"
}
```

A later fix and passing verification can reference the same finding.

Identity makes closure mechanical.

<!--
Without stable identity, a system cannot establish that
each finding received a repair and recheck.
-->

<!-- Clock 02:53 | 2 min -->

---

# Acceptance rule

> The role that produced the completion claim does not accept it.

The checker evaluates:

- Planner present
- Checker present
- Every edit inside declared scope
- Acceptance owned by checker

<!-- Clock 02:55 | 3 min -->

---

# M4 exercise — Enforce the plan

```sh
python m4_independent_acceptance/exercises/check.py
```

The planner's scope means nothing if nobody enforces it. Write the
**scope guard** a Claude Code `PreToolUse` hook runs before every edit:

1. `decide(event, project, plan)` in `guard.py`: allow or block, with a reason
2. `guard_cases.json`: your tests, cases it must **block** *and* must **allow**

The check then runs your tests against five deliberately **broken guards**.
Each one must fail at least one of your cases.

<!--
Run the first check.py live. The starter suite only lists what to block, so
"blocks everything" survives it. Ask: what would that guard do to the agent?
-->

<!-- Clock 02:58 | 3 min -->

---

# M4 exercise — Work time: a guard and its tests

| Check | Asks |
| --- | --- |
| `guard-function-contract` | Does your guard decide 13 hidden cases correctly? |
| `cases-both-directions` | At least 3 must-block **and** 3 must-allow cases? |
| `cases-agree-with-reference` | Is every expectation in your suite right? |
| `cases-catch-mutants` | Does each broken guard fail one of your cases? |

The broken guards: allows everything · blocks everything · blocks tools that
don't edit · no exemption for state files · matches paths by prefix.

<!--
Leave this slide up. At minute 10, hint: kb/kb.py.bak and docs_extra/ are the
prefix traps. One-sided tests let a guard drift toward blocking everything.
-->

<!-- Clock 03:01 | 12 min -->

---

# M4 exercise — Stretch: close the findings loop

Implement `open_findings(events)`, the capstone's `findings-addressed` rule:

```text
finding(id) → later fix(id) → passing verification after that fix
```

Still open when:

- No later fix carries the same id
- The only fix came before the finding
- The only passing verification came before the fix
- The verification after the fix failed

```sh
python m4_independent_acceptance/exercises/check.py --stretch
```

<!--
The capstone scorer uses exactly this rule. Pairs who finish can predict
which ladder rung would fail without it.
-->

<!-- Clock 03:13 | 7 min -->

---

# M4 exercise debrief

- What can a checker prove without a plan, and what can a guard enforce?
- Why must a guard's tests include what it must **allow**?
- Your guard can't see `echo x > notes.md`. What catches that?
- Who accepts completion in your current system?

<!-- Clock 03:20 | 5 min -->

---

<!-- _class: section -->

# Capstone

## Hold maker behavior constant

<!-- Clock 03:25 | 0 min -->

---

# Predict before running

For each configuration, predict:

| Predicate | Single-role | Gen-eval | Plan-gen-eval |
| --- | --- | --- | --- |
| Verification before done | ? | ? | ? |
| Evidence true | ? | ? | ? |
| Findings addressed | ? | ? | ? |
| Scope fidelity | ? | ? | ? |
| Clean state | ? | ? | ? |

<!--
Let pairs fill this mentally or on paper, then run the
ladder. Prediction makes the demo an assessment rather than a reveal.
-->

<!-- Clock 03:25 | 3 min -->

---

# Run the ladder

```sh
python m4_independent_acceptance/demos/01_ladder.py
```

Read failed predicate lists first.

Interpret scores only after understanding the failures.

<!--
Switch to the terminal. Ask participants to predict the one predicate gen-eval
will still fail before showing the output.
-->

<!-- Clock 03:28 | 2 min -->

---

# Same maker, different harness

| Configuration | Failed predicates | Score |
| --- | --- | ---: |
| Single-role | All five | 0 |
| Gen-eval | Scope fidelity | 4 |
| Plan-gen-eval | None | 5 |

The scores are counts of executable predicates.

They are not subjective quality ratings.

<!-- Clock 03:30 | 1 min -->

---

# Read the details, not only the scores

```text
gen-eval  4/5
  PASS findings-addressed   3 findings closed by fix and re-verification
  FAIL scope-fidelity       no plan declared scope; git shows:
                            config/retrieval-notes.md,
                            kb/kb.py, kb/test_kb.py
plan-gen-eval  5/5
  PASS scope-fidelity       flagged and reverted: config/retrieval-notes.md
```

Every run is a real git project under `m4_independent_acceptance/demos/runs/<config>/project/`.

<!--
Open m4_independent_acceptance/demos/runs/gen-eval/project/config/retrieval-notes.md: the
out-of-scope file shipped. In plan-gen-eval it is gone, and transcript.json shows who found it.
Scope is read from `git status` in each project, never from the maker's transcript; the
optional demo 03_self_report_vs_diff.py shows why.
-->

<!-- Clock 03:31 | 1 min -->

---

# Now run it with your predicates

```sh
python m4_independent_acceptance/demos/02_ladder_with_your_code.py
```

| Rubric item | Your code |
| --- | --- |
| evidence-true | M2 exercise `reproduce` |
| clean-state | M3 exercise `resume_ready` |
| scope-fidelity | M1 exercise stretch `scope_violations` |
| findings-addressed | M4 exercise stretch `open_findings` |

Unimplemented pieces fall back to the reference.

A lenient predicate moves a rung: the starter's readiness check scores `1 -> 4 -> 5`.

<!--
Ask who got exactly 0 -> 4 -> 5. Then ask anyone whose output says
"its check FAILS" why the ladder still looked right: a rubric only
catches what the run exercises.
-->

<!-- Clock 03:32 | 2 min -->

---

# What changed?

The maker did not improve.

The harness added:

1. Executed verification
2. Reproduced evidence
3. Findings and repair
4. Clean-state enforcement
5. Declared scope
6. Independent acceptance

Reliability came from system design.

<!-- Clock 03:34 | 1 min -->

---

# Live: same agent, with the harness

```sh
python instructor/live/score_project.py ../live-off ../live-on
```

Same model, same prompt. What changed is all in files:

- `plan.json`: scope, plus an acceptance command the planner owns
- A `PreToolUse` hook that blocks edits outside that scope
- A `Stop` hook that runs the done gate before "done"

Two runs are a demo, not an eval.

<!--
Open the transcript where the Stop hook blocked, and read the fix lines the agent received.
-->

<!-- Clock 03:35 | 7 min -->

---

# Which control is load-bearing?

Every control encodes an assumption about what the model *can't* do.

```sh
python m4_independent_acceptance/gate.py --explain
python instructor/live/score_project.py ../live-on ../live-no-stop
```

- **Contract** controls define done: they never expire.
- **Compensating** controls work around today's model: remove them when they stop earning their place.

Ask of every harness: *what can I stop doing?*

<!--
Show --explain, then the pre-recorded --without stop-gate ablation. One run per
arm shows a mechanism; measuring one needs 20 to 50 frozen tasks with one
control removed at a time. Anthropic's example: context resets built for one
model became dead weight on the next.
-->

<!-- Clock 03:42 | 3 min -->

---

<!-- _class: section -->

# Transfer

## One predicate for your repository

<!-- Clock 03:45 | 0 min -->

---

# A practical adoption order

Start with the failure you already observe:

1. Add one durable state artifact
2. Add one executable predicate
3. Gate one state transition on that predicate
4. Add startup and exit checks
5. Separate acceptance
6. Add scope comparison

Do not begin by designing a universal harness platform.

<!--
Encourage a thin vertical slice around one recurring
failure instead of a large framework migration.
-->

<!-- Clock 03:45 | 2 min -->

---

# Build your transfer card

Choose one real failure:

- Failure to prevent
- Durable input artifact
- Executed command
- Passing observation
- Failing observation
- Role allowed to accept
- Where the predicate runs

Your partner must challenge whether the command really establishes the claim.

<!--
Pair participants after five minutes. Collect the cards
as the practical output of the class.
-->

<!-- Clock 03:47 | 5 min -->

---

# Test the transfer predicate

Ask of your proposed command:

1. Can a fresh process execute it?
2. Does non-zero remain a failure?
3. Does it observe the claimed property directly?
4. Can a stale or fabricated record be detected?
5. Is the output stable enough to compare?
6. Who acts when it fails?

If any answer is unclear, the predicate is not finished.

<!--
Partners use these questions to
challenge each other's cards.
-->

<!-- Clock 03:52 | 3 min -->

---

# Exit check

Answer without notes:

1. What is the difference between a completion claim and evidence?
2. What state must survive the end of a session, for whoever comes next?
3. What can a planner make visible that a checker alone cannot?

<!-- Clock 03:55 | 4 min -->

---

<!-- _class: lead -->
<!-- _header: "" -->
<!-- _footer: "" -->

# Move truth out of the transcript

Into artifacts and commands the next session can inspect.

```sh
python instructor/verify_all.py
```

<!--
Close by returning to the repository gate. A capable agent plus an
unverifiable repository is still an unreliable system.
-->

<!-- Clock 03:59 | 1 min -->

---

<!-- _class: section -->

# Appendix

## Deep dives and post-lab reference

Not part of the timed 240-minute path.

<!--
Use these for questions or self-study. Three slides show lab solutions (the
WIP bound, the verifier, the handoff parser): show them only after the lab.
-->

---

# The 240-minute run

| Segment | Minutes |
| --- | ---: |
| Framing, baseline diagnosis, and the bare live run | 30 |
| Scope and state teaching + M1 exercise | 40 |
| Evidence teaching + M2 exercise | 43 |
| Break | 10 |
| Continuity teaching + M3 exercise | 40 |
| Role separation teaching + M4 exercise | 42 |
| Capstone ladder, harnessed live run, transfer, and exit check | 35 |
| **Total** | **240** |

<!--
This is the full class contract. Lab time is part of the
deck: the lab slides remain projected with checkpoints and hints.
-->

---

# What this class assumes

You already work with:

- Agent frameworks and tool calling
- MCP, A2A, LangGraph, ADK, or equivalent systems
- Automated tests and CI
- Repository-based engineering workflows

We will not explain those foundations.

We will engineer the reliability layer around them.

<!--
This prevents the class from drifting into agent
fundamentals. The audience should recognize all listed concepts.
-->

---

# What harness engineering is not

It is not:

- A prompt library
- Another orchestration framework
- A larger context window
- A retry policy
- A benchmark
- A substitute for capable models

It is the system that makes work **bounded, inspectable, and verifiable**.

<!--
Ask which item participants have previously mistaken for a
harness. Clarify that these can be components but do not establish truth.
-->

---

# The task's observable contract

For `delete(document_id)`:

| Observable | Required result |
| --- | --- |
| Source file | Removed |
| Metadata entry | Removed |
| Remaining documents | Still readable |
| Unknown ID | Explicit failure |
| Verification | Re-executable |

“The function returned” is not the contract.

<!--
Ask which row a code review might miss. Derived-state
consistency is the bridge into the baseline failure.
-->

---

# A useful diagnostic question

When agent work fails, ask:

> What information, boundary, durable state, or executable feedback was
> missing from the system?

Do not start with:

> Which model should we use instead?

<!--
This question is reused in every debrief. It redirects
failure analysis from capability speculation to system design.
-->

---

# The maker said “done”

The repository said:

```text
FAIL verification-before-done
FAIL evidence-true
FAIL findings-addressed
FAIL scope-fidelity
FAIL clean-state
```

> “Done” is an event in a transcript.
> It is not a property of the repository.

---

# Instructions — route, do not dump

Useful instructions answer:

- Where is product behavior defined?
- Where is architecture defined?
- Which commands establish readiness and completion?
- Which local rules apply to this directory?

A short router beats one giant instruction file.

<!--
Explain that instructions should point to authoritative
state rather than duplicate it into a prompt-shaped document.
-->

---

# Tools — actions plus truthful observations

A tool surface should make important state inspectable:

```text
reset
doctor
observe
check
status
```

Tools are not valuable because the agent can call them.

They are valuable because their outputs support predicates.

<!--
Contrast a mutation-only API with one that exposes status
and verification commands.
-->

---

# Environment — refuse bad starting conditions

Before work begins, the doctor checks:

- Router targets resolve
- Feature states are valid
- WIP limit holds
- Passing features carry evidence
- Handoff has required sections

Fail early, before the session creates more state.

<!--
Ask what their current repositories check before an agent
starts, not merely what CI checks afterward.
-->

---

# State — move truth out of context

Durable state includes:

- Current feature and status
- Declared scope
- Verification evidence
- Known failures
- Next bounded action

If it matters after interruption, it should not exist only in the transcript.

<!--
Context can cache state, but the repository remains the
authority that another process can inspect.
-->

---

# Feedback — produce repairable failure

Good feedback is:

- Specific: names the failed predicate
- Local: points to the relevant artifact
- Executable: can be rerun
- Comparative: expected versus observed
- Non-success-shaped: failures remain failures

“Something went wrong” cannot drive a repair loop.

<!--
Read one starter failure from a lab and show how it names
the mechanism rather than merely returning exit 1.
-->

---

# Diagnose before prescribing

| Symptom | Likely subsystem |
| --- | --- |
| Agent edits unrelated files | Instructions or state |
| New session restarts discovery | State |
| Works locally, fails in CI | Environment |
| Claims done without execution | Feedback |
| Cannot inspect derived state | Tools |

The subsystem identifies where the repair belongs.

<!--
Ask participants for one symptom and classify it together.
Multiple subsystems can contribute; choose the first enforceable repair.
-->

---

# Passing requires evidence

```json
{
  "id": "delete-command",
  "status": "passing",
  "evidence": {
    "command": "kb ask deletion",
    "observed": "{...}"
  }
}
```

No evidence → not `passing`.

<!--
The feature file is not the authority over product truth.
It is a cache whose transition must be justified by execution.
-->

---

# The WIP predicate we need

```python
len(active) <= 1
```

Why allow zero?

- Between work items
- After clean completion
- When all remaining work is blocked

The invariant is a bound, not a requirement to stay busy.

<!--
This contract case is included because a hard-coded
`len(active) == 1` creates a new invalid state at session completion.
-->

---

# The verifier must use actual output

```python
exit_code, observed = execute(command)

passed = (
    exit_code == 0
    and observed == evidence["observed"]
)
```

Never return the recorded output as though it were newly observed.

<!--
This is the starter defect in the M2 exercise. It trusts and echoes
the claim instead of invoking the executor.
-->

---

# Review and execution are complementary

| Property | Best first check |
| --- | --- |
| Function returns expected shape | Execution |
| Metadata index matches source files | Execution |
| Naming communicates intent | Review |
| Architecture trade-off is justified | Review |
| No unrelated paths changed | Execution against plan |

Do not make reviewers simulate a command the repository can run.

<!--
This keeps the class from implying that automated
verification replaces engineering judgment.
-->

---

# Evidence anti-patterns

```text
"tests passed"
"reviewed manually"
"exit 0: assumed"
"worked earlier"
"looks correct"
```

These may be useful notes.

They are not reproducible observations.

<!--
Ask participants which of these appears in their current
agent-generated handoffs or pull-request descriptions.
-->

---

# Parsing the handoff

```python
if line.startswith("## "):
    current = line[3:].strip()
    sections[current] = []
elif current and line.startswith("- "):
    sections[current].append(line[2:].strip())
```

Simple format, deterministic behavior, inspectable state.

<!--
The point is not Markdown parsing sophistication. The
point is a format both humans and the harness can read.
-->

---

# Why preserve unknown sections?

A future session may add:

```md
## Risks
## Decisions
## Rollback notes
```

An older reader can still:

- Enforce required sections
- Preserve additive information
- Avoid destructive rewrites

Extension should not require a parser fork.

<!--
Connect this to forwards-compatible schemas: strict on
required semantics, tolerant of additive fields.
-->

---

# Planner responsibility

The planner declares:

- Work item
- Allowed scope
- Required predicates
- Expected completion boundary

The planner does **not** prove the implementation works.

It makes intent inspectable before edits exist.

<!--
A plan written after the edits cannot serve as an
independent scope declaration.
-->

---

# Maker responsibility

The maker:

- Selects the bounded next action
- Changes allowed files
- Records what it changed
- Requests verification
- Repairs checker findings

The maker may report completion.

It does not accept that report.

<!--
This separation avoids asking the generator to switch
magically from advocacy to independent judgment.
-->

---

# Checker responsibility

The checker:

- Executes required predicates
- Reproduces evidence
- Compares edits with declared scope
- Emits specific findings
- Rechecks after repair
- Accepts or rejects final state

The checker evaluates repository truth, not maker confidence.

<!--
The checker needs tools and state, not merely a different
prompt saying “be critical.”
-->

---

# Gen-eval flow

```text
maker output
    ↓
checker executes rubric
    ↓
findings
    ↓
maker repairs
    ↓
checker re-executes
```

This catches false completion.

It does not create missing intent.

<!--
Gen-eval is valuable; the limitation is specific to scope
because no artifact declares the comparison boundary.
-->

---

# What did not change?

- Same work item
- Same maker behavior
- Same three flaws
- Same repository
- Same deterministic fixture

Holding these constant makes the harness effect inspectable.

<!--
This is a controlled teaching experiment, not a benchmark
claim about models or production performance.
-->

---

# Common adoption mistakes

- Copying templates without connecting them to commands
- Recording evidence that nobody re-executes
- Adding roles without defining responsibilities
- Treating a passing test suite as scope fidelity
- Storing progress only in chat history
- Making doctor failures warnings

Mechanisms matter only when wired into decisions.

<!--
Ask which mistake is most likely in the participant's
organization. Use the answer to frame the transfer exercise.
-->

---

# 2026: what changed, and what's contested

| Claim | Status |
| --- | --- |
| Rules in prose get followed | Rarely: one study found 4–16% of security rules in `CLAUDE.md` files had any effect. Enforce with hooks, linters, CI |
| Context resets fix long tasks | Dead weight on newer models. What helps is state written to files |
| Add a reviewer agent | Reported to *lower* success in one ablation; prefer computational sensors |
| Agent teams beat one agent | Roughly equal on SWE-bench in one study; >4 handoffs usually failed (Microsoft) |
| Ask the user before risky actions | 93% of permission prompts get approved; a rule that ends in "ask" isn't a rule |

<!--
Sources: Marmelab, "The State of AI Harness Engineering 2026" (2026-09-24), which
cites the underlying studies; Anthropic, "Harnessing Claude's intelligence".
Treat magnitudes as reported, not reproduced.
-->

---

# Permissions and sandboxing

- **Deny rules** restrict whatever the agent asks for: `Edit(/plan.json)`, `Edit(/.harness/**)`
- **Hooks** add logic deny rules can't express, and block with exit code 2
- **Allow rules** in project settings apply only after you trust the folder
- Neither sees a script that opens files itself: **sandbox** the process for OS-level limits
- Promote risky or hard-to-reverse actions to **dedicated tools** the harness can gate, log, and audit

<!--
The live project's .claude/settings.json uses deny rules plus two hooks. Claude
Code docs: permissions, hooks, sandboxing. Anthropic recommends dedicated tools for
security, UX, and observability boundaries.
-->

---

# Context and tools are part of the harness

- The harness decides what enters the model's context: keep `AGENTS.md` around 100 lines, a map
- Machine-generated context files were reported to *reduce* task success; human-written ones helped a little
- Fewer tools often help: one team reported higher success and half the tokens after removing most tools
- **Skills** load only when needed (progressive disclosure); **subagents** get a fresh context for one task

<!--
Sources: OpenAI harness engineering (~100-line AGENTS.md); ETH Zurich study on
context files and Vercel's tool reduction, both as reported by Marmelab; Anthropic,
"Harnessing Claude's intelligence" (skills, subagents, context editing).
-->

---

# Observe the harness in use

An eval tells you whether a change helps on tasks you picked. Real sessions tell you:

- Which hooks fire, and how often they block
- Which skills and tools actually get used
- How many iterations a task takes

Start small: log hook decisions to a file, keep transcripts, read some of them.

<!--
Only 5 of 391 repositories Marmelab audited record anything about harness use.
The VS Code team runs offline evals before shipping and keeps measuring after,
with A/B tests and weekly reporting. instructor/live/score_project.py tallies
tool calls from a Claude Code stream-json transcript.
-->

---

# Throughput changes the answer

- Low volume: block merges on every check; a bad merge is expensive
- High volume: few mandatory checks, short-lived PRs, re-run flaky tests; a blocked queue is expensive
- OpenAI: "corrections are cheap, and waiting is expensive", and irresponsible at low throughput

Decide per repository which controls block and which only report.

<!--
Source: OpenAI, "Harness engineering" (as quoted by Marmelab). This workshop
deliberately blocks on everything, because it teaches the controls themselves.
-->

---

# Behavior is the hardest harness

Böckeler's three kinds of harness:

| Harness | Example sensors | Maturity |
| --- | --- | --- |
| Maintainability | lint, complexity, coverage, structural tests | Most mature |
| Architecture fitness | fitness functions, performance tests | Growing |
| Behavior | specs, tests, **acceptance checks**, manual testing | Hardest |

AI-written tests aren't trustworthy enough on their own; that's why this class
uses planner-owned acceptance checks and a hidden eval.

<!--
Also from Böckeler: "harnessability". Typed languages and clear module
boundaries make more controls possible; legacy code needs them most and makes
them hardest to build.
-->

---

# Sources

- Böckeler, "Harness engineering", martinfowler.com
- OpenAI, "Harness engineering: leveraging Codex in an agent-first world" (Feb 2026)
- Anthropic, "Effective harnesses for long-running agents"; "Harness design for long-running application development"; "Harnessing Claude's intelligence"
- Marmelab, "The State of AI Harness Engineering 2026" (Sep 2026)
- VS Code team, "The coding harness behind GitHub Copilot in VS Code" (May 2026)
- Claude Code documentation: hooks, permissions, memory
