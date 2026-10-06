# Facilitator script

This script is designed for one instructor and an experienced engineering
audience. Quoted lines are suggested language, not text that must be read
verbatim.

## 00:00–00:10 — Contract and framing

Say:

> Today the agent does not get smarter. We hold its behavior constant and
> change the execution system around it. If the outcome improves, we can
> attribute that improvement to the harness.

Ask for two recent examples where an agent was capable of the local edit but
the overall task still failed. Capture only the failure shape: drift, lost
state, unverified completion, environment mismatch, or missing feedback.

Do not define agents, orchestration, tools, or evals.

Before you start talking, start the **bare** live run in a second terminal:
`cd ../live-off`, `claude`, then the prompt `Implement document deletion end to end.`
Let it work while you frame the class. See `instructor/live/RUNBOOK.md`; build
the projects and record a fallback the day before.

Transition:

> Our work item is document deletion. It sounds small enough to trust and is
> stateful enough to punish that trust.

## 00:10–00:25 — Baseline demo

Run:

```sh
python m1_scope_and_state/demos/01_baseline_failure.py
```

The non-zero exit is intentional. The output has five blocks: what the maker
did, the `delete()` it actually wrote, what it recorded, what is actually true
when the commands are re-executed now (including `git status`), and the
rubric. Point at the contradiction first: `documents/` holds two files while
`kb list` still indexes three, and `kb ask deletion` exits 1. The maker's
claim says "listing unaffected". Then point at its `delete()`: it never
touches the index.

Then read each failed rubric line and ask the room to classify it under
the two axes on the "Agent = Model + Harness" slide: was the missing control a
**guide** (before the agent acts) or a **sensor** (after)? Computational or
inferential? The run is a real git
project in `m1_scope_and_state/demos/runs/single-role/project/` for anyone
who wants to open the code, the index, or `git diff`.

Key point:

> "Done" is an event in a transcript. It is not a property of the repository.

If participants jump to better prompting, ask which prompt establishes that
the derived index is consistent after the process exits.

## 00:25–00:30 — Live: the bare agent

Run `python instructor/live/score_project.py ../live-off`. Read the **hidden
eval** first. These are cases the agent never saw: did delete really work?
Then the **done gate**: could the repository prove it? A bare repository has
no plan, feature list, or handoff, so the gate fails even when the code works.

If the bare run passed the hidden eval, say so: "The harness's value here will
be proof, not rescue." If it failed, name the cause before moving on.

## 00:30–00:45 — Scope and durable state

Open the M1 exercise starter feature list and plan. Contrast:

- A backlog item: an intention.
- `in-progress`: an ownership claim on the next action.
- Allowed paths: a declared comparison boundary.
- A next action: the smallest resumable unit.

Explain WIP=1 as a harness policy, not a universal team-process claim. Here it
exists to stop one agent session from opening more state than it can settle.

If time allows (3 minutes), run `python m1_scope_and_state/demos/03_scope_guard.py`.
It shows the same scope rule as a Claude Code `PreToolUse` hook: the JSON
Claude Code sends, then exit 0 (allow) or exit 2 (block) with the reason Claude
reads. Make one point: a rule written in prose is often ignored, but an exit
code isn't. Then show its last block: a shell command writes a file the guard
never sees, and `git status` catches it. Neither check is enough on its own.

## 00:45–01:10 — M1 exercise

Participants run:

```sh
python m1_scope_and_state/exercises/check.py
```

They must:

1. Fix the feature state so at most one item is active.
2. Declare allowed paths and a bounded next action in `plan.json`.
3. Implement `assess_scope` so it handles zero, one, and multiple active
   features and rejects empty scope.

Block shape: 3 min brief, 12 min core, 5 min stretch window, 5 min debrief.

At 10 minutes into core work, offer the hint: predicates should test truth,
not key presence. Pairs who pass the core move to the stretch
(`check.py --stretch`); pairs still on the core keep going. Start the
debrief on time either way.

Debrief:

- Why does `bool(active)` fail as a WIP limit?
- What could enforce scope against actual Git changes?
- Which artifact survives a new session?

## 01:10–01:25 — From claims to evidence

Show the assumed observation in the M2 exercise. Ask whether command text alone is
evidence. Establish the tuple:

```text
command + exit + observed output
```

Then add the critical operation: the checker re-executes the command and
compares what it observes now.

Say:

> Evidence is not trustworthy because it is structured. It is trustworthy
> when another process can reproduce it.

## 01:25–01:53 — M2 exercise

Participants run:

```sh
python m2_executable_verification/exercises/check.py
python m2_executable_verification/demos/01_observe.py
```

They must:

1. Implement `reproduce` using the injected executor.
2. Preserve the actual exit and observed output in the report.
3. Pass only when exit is zero and observed output exactly matches recorded
   evidence.
4. Replace the assumed observation in the working feature list.

Block shape: 3 min brief, 15 min core, 5 min stretch window, 5 min debrief.

At 10 minutes into core work, ask why unsupported commands must remain
explicit failures. Pairs who pass the core move to the structural-lint stretch
(`check.py --stretch`). It's a sensor that reads the code before anything runs,
and it puts its fix in the message.

Debrief:

- Why execute through an injected function?
- Which evidence fields are assertions and which are observations?
- When would exact output be too strict, and where would normalization belong?

## 01:53–02:03 — Break

Leave the successful M2 exercise output visible.

## 02:03–02:18 — Continuity

Ask participants what a new session knows if the previous transcript is gone.
Widen the question: the next reader might be a fresh agent, a parallel agent,
a teammate, or you tomorrow. Don't frame this as context-window management.
Newer models largely don't need context resets. What still matters is that
the state is written down. Open the handoff starter. Establish the three
required claims:

- Verified now.
- Broken or unverified.
- Next best step.

Explain why unknown sections must round-trip: extension should not require
forking the parser, while required sections remain a hard readiness gate.

Then run `python m3_continuity/demos/03_next_session.py` (3 minutes). Session
2 inherits session 1's false record. Without a doctor, its new import fails on
the project's data and *looks* like its own bug; the cause is session 1's
delete. With a doctor, it refuses to start on a lie, repairs first, and import
works on the first try. Ask: "Who would have debugged the wrong code, and for
how long?"

## 02:18–02:43 — M3 exercise

Participants run:

```sh
python m3_continuity/exercises/check.py
```

They must:

1. Parse `##` sections and their list items.
2. Preserve unknown sections.
3. Return required sections in deterministic missing-order.
4. Add a bounded next step to the handoff artifact.

Block shape: 3 min brief, 12 min core, 5 min stretch window, 5 min debrief.
Pairs who pass the core move to the round-trip stretch
(`check.py --stretch`).

Debrief:

- Why is "everything is fine" a bad handoff?
- Why should the doctor run before work begins?
- What belongs in durable state rather than prompt context?

## 02:43–02:58 — Role separation

Draw three boxes: planner, maker, checker.

Ask:

> If the checker executes every test, can it detect an unrelated file edit?

The answer is no unless scope was declared before making. This is the
distinction between gen-eval and plan-gen-eval.

State the acceptance rule:

> The role that produced the completion claim does not accept it.

Then make it mechanical (3 minutes): run
`python m4_independent_acceptance/demos/04_stop_gate.py`. The baseline says
"delete works" and tries to stop. The Claude Code `Stop` hook runs the done
gate, exits 2, and Claude would read every failure with its fix line. Point
out that `tests-pass` is **not** among the failures: the maker wrote no delete
test. Only the re-executed evidence catches the bug.

Add one point about current practice: the checker here is a script. An LLM
reviewer agent is a weaker sensor, and studies reported in late 2026 found
that adding one can lower success rates. Prefer code wherever the check can
be computed.

## 02:58–03:25 — M4 exercise

Participants run:

```sh
python m4_independent_acceptance/exercises/check.py
```

They must:

1. Implement `decide(event, project, plan)` in `guard.py`: the scope guard a
   Claude Code `PreToolUse` hook runs before every edit. It follows the seven
   rules in its docstring.
2. Turn `guard_cases.json` into a two-sided suite: at least 3 cases the guard
   must block **and** 3 it must allow, every expectation correct.
3. Make sure each of the five broken guards fails at least one case.

Block shape: 3 min brief, 12 min core, 7 min stretch window, 5 min debrief.

While pairs work, start the **harnessed** live run in `../live-on` (same prompt).

At 10 minutes into core work, offer the hint: `kb/kb.py.bak` and `docs_extra/`
are the prefix traps, and a suite with no must-allow cases can't tell a
working guard from one that blocks everything. Pairs who pass the core move to
the findings stretch (`check.py --stretch`), which is the rule the capstone
ladder uses.

Debrief:

- What can a checker prove without a plan, and what can a guard enforce?
- Why must a guard's tests include what it must allow?
- The guard can't see a shell command's edits. What catches them? (`git status`
  in the done gate: defense in depth.)

## 03:25–03:35 — Capstone ladder

Run:

```sh
python m4_independent_acceptance/demos/01_ladder.py
```

Read failed lists first:

- Single-role fails all five.
- Gen-eval repairs verification, evidence, findings, and clean state.
- Plan-gen-eval adds scope fidelity.

Only then discuss the scores. They are counts of predicates, not quality
ratings. Open `m4_independent_acceptance/demos/runs/gen-eval/project/config/retrieval-notes.md` to show the
out-of-scope edit that shipped, then the plan-gen-eval transcript to show who
found and reverted it.

Then have everyone run the ladder with their own exercise code:

```sh
python m4_independent_acceptance/demos/02_ladder_with_your_code.py
```

Their `reproduce`, `resume_ready`, and (if done) the two stretch functions now
score the rubric; anything unimplemented falls back to the reference. Ask who
got exactly `0 -> 4 -> 5`. If anyone's output says "its check FAILS" yet
the ladder looked right, use it: a rubric only catches what the run exercises.
If nobody has a lenient predicate, demonstrate one by resetting M3 exercise to its
starter (`git checkout -- m3_continuity/exercises`); the ladder moves to `1 -> 4 -> 5`.

## 03:35–03:45 — Live: same agent, with the harness

Run `python instructor/live/score_project.py ../live-off ../live-on`. Same model,
same prompt. Trace every difference to a file: `plan.json` and its acceptance
command, the scope guard, and the Stop gate. Open the transcript where the
Stop hook blocked, and read the fix lines the agent received. (7 minutes.)

Then the prune beat (3 minutes, slide "Which control is load-bearing?"). Run
`python m4_independent_acceptance/gate.py --explain`: contract controls define
done and never expire; compensating controls work around today's model. Show
the pre-recorded `--without stop-gate` ablation. Ask: "What can you stop doing?"

Close with: "Two runs are a demo, not an eval. To know whether a control earns
its place, freeze 20 to 50 tasks and remove one control at a time. That's how
you keep a harness small as models improve."

## 03:45–03:55 — Transfer

Participants complete the transfer card in the Module 4 README. Pair them and require
the partner to challenge whether the proposed command really establishes the
claimed property.

## 03:55–04:00 — Exit check

Ask the three exit-check questions from the Module 4 README. Close with:

> A capable agent plus an unverifiable repository is still an unreliable
> system. Harness engineering moves truth out of the transcript and into
> artifacts and commands the next session can inspect.

Collect the transfer cards as the class output.
