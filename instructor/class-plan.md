# Four-hour class plan

This is the delivery contract for the live class. The minute allocations are
planning heuristics. They sum to 240 minutes, including one 10-minute break.

## Outcomes

By the end, participants can:

1. Attribute an agent failure to a missing guide or sensor, computational or
   inferential, instead of calling it a model failure.
2. Enforce explicit scope and one item in progress.
3. Promote feature state only from reproducible command evidence.
4. Design startup and handoff checks that let a new session resume from the
   repository alone.
5. Separate planning, making, and acceptance with executable predicates,
   and test a guard in both directions.
6. Transfer one mechanism into a repository they already own.
7. Enforce a check inside an agent's loop with a hook, not only after it.

## Agenda

| Clock | Minutes | Activity | Mode | Evidence of learning |
| --- | ---: | --- | --- | --- |
| 00:00 | 10 | Frame the problem and establish the class contract; start the bare live agent run | Discussion | Participants name failures that were not capability failures |
| 00:10 | 15 | Run and diagnose the unchecked baseline | Demo | Each failed predicate is traced to a missing guide or sensor |
| 00:25 | 5 | Score the bare Claude Code run: hidden eval, then done gate | Live demo | Participants separate "did it work" from "can the repository prove it" |
| 00:30 | 15 | Teach scope, durable state, and WIP=1 | Explain + inspect | Participants distinguish backlog from executable state |
| 00:45 | 25 | M1 exercise: implement the scope gate | Pair coding | Contract cases and repaired artifact pass |
| 01:10 | 15 | Teach claims, observations, and independent re-execution | Explain + demo | Participants identify fabricated evidence |
| 01:25 | 28 | M2 exercise: implement evidence reproduction | Pair coding | Real observation replaces assumed output |
| 01:53 | 10 | Break | | |
| 02:03 | 15 | Teach repository readability and continuity | Explain + inspect | Participants identify minimum resumable state |
| 02:18 | 25 | M3 exercise: implement handoff parsing and readiness | Pair coding | Unknown sections survive and required sections gate readiness |
| 02:43 | 15 | Teach maker, checker, planner, and acceptance boundaries | Explain + debate | Participants identify what gen-eval cannot detect |
| 02:58 | 27 | M4 exercise: enforce the plan with a scope-guard hook and a two-sided test suite; start the harnessed live run | Pair coding | Guard contract cases pass and the suite catches every broken guard |
| 03:25 | 10 | Run the 0 → 4 → 5 ladder, then again with participants' own predicates | Demo + debrief | Failed predicates, not scores, explain each rung |
| 03:35 | 10 | Score the harnessed Claude Code run beside the bare one | Live demo | Participants trace each difference to a file in the harness |
| 03:45 | 10 | Individual transfer design | Solo | Each participant writes one predicate for a real repository |
| 03:55 | 5 | Exit check and close | Assessment | Participants answer the three exit prompts |

## Delivery constraints

- Do not explain agent frameworks. The audience already uses them.
- Do not let the class become a repository tour. Stay with the delete work
  item throughout.
- Read failed predicate names before reading scores.
- Never accept a verbal "done"; ask which command established it.
- Keep solutions closed until pairs can state the failed invariant.
- If time compresses, cut stretch windows first, then appendix-only
  discussion, never the core implementation tasks or debriefs.

## Exercise block structure

Every exercise block has four parts: a 3-minute brief, core work time, a stretch
window, and a 5-minute debrief. The core task is required. The stretch is a
checked extension (`check.py --stretch`) for pairs who finish the core
early, so the block does not depend on everyone working at the same speed.

## Slide deck

[slides.md](slides.md) is the delivery deck. Every slide before the
`Appendix` divider carries a `Clock HH:MM | N min` presenter note. A test
checks that those clocks run without gaps from 00:00 to 04:00 and that every
agenda row above starts on a slide. Appendix slides are untimed deep dives and
post-lab reference.

## Timing honesty

The agenda is machine-checked to sum to 240 minutes, and the deck is
machine-checked to follow it. Neither has been validated by a timed delivery.
Record actual segment durations at the first pilot (see
[assessment](assessment.md)) and adjust.

## Completion standard

The class is complete when every participant has:

- Passed all four exercise checks.
- Explained why the baseline's completion claim is invalid.
- Explained why gen-eval still misses scope drift.
- Written one repository-specific predicate with its input, command, expected
  observation, and owner.
