# Assessment

## Formative checks

Each module's exercise check is the primary formative assessment. Passing requires both:

- A repaired repository artifact.
- A Python implementation that passes multiple contract cases.

The committed starter must fail on the exact recorded predicates; the
committed solution must pass all predicates.

Stretch tasks (`check.py --stretch`) are optional and do not count
toward the completion standard. Record how many pairs reach each one: that is
the most direct signal of whether core lab time is too long or too short.

## Capstone rubric

Score each dimension as demonstrated or not yet demonstrated. Do not weight or
average the dimensions.

| Dimension | Demonstrated when |
| --- | --- |
| Failure attribution | Names the missing control, and whether it is a guide or a sensor, computational or inferential |
| Scope control | Declares allowed scope and enforces WIP=1 |
| Evidence | Re-executes a command and compares exit plus observation |
| Continuity | Preserves verified, unverified, and next-step state |
| Independent acceptance | A checker, not the maker, accepts against declared scope |
| Transfer | Writes an executable predicate for a real repository |

## Exit prompts

1. What is the difference between a completion claim and evidence?
2. What state must survive the end of a session, for whoever comes next?
3. What can a planner make visible that a checker alone cannot?

## Answer guide

1. A claim is an event produced by a role. Evidence is an observation produced
   by executing a command whose result can be independently reproduced.
2. Scope, current feature state, verified evidence, unresolved failures, and
   the bounded next action must be readable from repository artifacts. The
   next reader may be a fresh agent, a parallel agent, or a person; none has
   the transcript, and a doctor should check the record before trusting it.
3. A planner declares intent and allowed scope before edits exist. Without
   that boundary, a checker can verify behavior but cannot distinguish
   intended edits from scope drift.

## Class success evidence

Retain only aggregate, non-sensitive results:

- Number of participants whose four exercise checks passed.
- Which contract case required the most hints.
- Whether each participant produced a transfer predicate.
- Actual segment durations from the pilot.
- Minutes into each exercise when each pair passed the core, and how many pairs
  passed each stretch.

Do not convert these into benchmark claims. They are delivery observations for
improving the next class.
