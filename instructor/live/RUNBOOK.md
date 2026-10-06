# Live segment runbook: Claude Code with and without the harness

The scripted ladder shows *why* each control matters. This segment shows a
real agent working under the same controls. It's instructor-run: students
need no Claude Code account or API key.

**Frame it honestly.** Two live runs are a demo, not an evaluation. Real
agents vary from run to run. A bare run may well succeed. If it does, the
lesson is that the harness's value here is *proof*, not rescue: only the
harnessed run can show that the work holds.

## What you need

- Claude Code, installed and logged in (`claude --version`).
- Python 3.12+ and Git on PATH.
- Two terminals, and a folder **outside** this repository for the projects.
  Claude Code loads every `AGENTS.md` in the working directory and above it,
  so a project inside the workshop would read the workshop's own instructions.
  The setup script refuses such a folder.

## Build the projects

Run these from the workshop root:

```sh
python instructor/live/setup_project.py ../live-off --harness off
python instructor/live/setup_project.py ../live-on  --harness on
```

| | `--harness off` | `--harness on` |
|---|---|---|
| The app (`delete` and `import` not built) | ✅ | ✅ |
| `AGENTS.md`, with `CLAUDE.md` importing it | | ✅ |
| `plan.json`: feature, acceptance command `kb delete-roundtrip`, allowed paths | | ✅ (committed by the "planner") |
| `feature_list.json`, `session-handoff.md`, `docs/` | | ✅ |
| `.harness/`: the workshop's own rules, gate, and hooks, plus `doctor.py`, `observe.py`, and `gate.py` | | ✅ |
| `.claude/settings.json`: `PreToolUse` scope guard, `Stop` gate, and deny rules on `.harness/`, `.claude/`, and `plan.json` | | ✅ |

For a one-control **ablation**, add `--without scope-guard`, `--without stop-gate`,
or `--without router` to the harnessed build.

## Rehearse the day before

1. Build both projects. In each, run the **same prompt**:
   `Implement document deletion end to end.`
2. In the harnessed run, open Claude Code's `/hooks` menu and confirm that both hooks are listed.
3. Score both from the workshop root:
   ```sh
   python instructor/live/score_project.py ../live-off ../live-on
   ```
4. **Record a fallback.** Run headless to save a transcript. Keep the transcript,
   the scorer output, and `git -C ../live-on log -p` in case the network or
   the agent fails in class.
   ```sh
   cd ../live-on
   claude -p "Implement document deletion end to end." --output-format stream-json --verbose > ../live-on.jsonl
   ```
   Check the flags against `claude --help` during rehearsal; the CLI evolves.
5. Pass the transcript to the scorer to see which tools the agent used, and
   whether it ran the gate itself. That is observing the harness in real use:
   ```sh
   python instructor/live/score_project.py ../live-on --transcript ../live-on.jsonl
   ```

### Permissions: two things that surprise people

- **Allow rules in `.claude/settings.json` apply only after you accept Claude Code's
  "trust this folder" dialog**, which appears in interactive sessions only. A headless
  `claude -p` run ignores them. Either run interactively and accept the dialog, or
  pass tool approvals on the command line (`--allowedTools`, `--permission-mode`).
- **Hooks and deny rules apply either way.** The scope guard, the Stop gate, and the
  deny rules on `.harness/` and `plan.json` are active in both modes. That's the point:
  enforcement doesn't depend on the agent's cooperation.

## In class

| Clock | Do | Say |
|---|---|---|
| ~00:05 | In terminal 2, start the **bare** run (`cd ../live-off`, then `claude`, then the prompt). Let it work while you frame the class | "A real agent is doing our task right now, with nothing around it." |
| 00:25–00:30 | Score it: `python instructor/live/score_project.py ../live-off` | Read the **hidden eval** first: did delete really work? Then the gate: could the repository prove it? |
| ~03:10 | During the M4 exercise, start the **harnessed** run in `../live-on` | — |
| 03:35–03:45 | Score both side by side. Open the transcript where the `Stop` hook blocked, and read the fix lines the agent received | "Same model, same prompt. The difference is the harness, and every part of it is a file you can read." |

If the bare run fails the hidden eval, point at the cause: usually the index,
exactly as in the scripted baseline. If it passes, point at the gate: nothing
in the bare repository proves it, and the next session would have to take its
word for it.

### Optional: the next session

After the harnessed run, act as the planner. In `../live-on`, edit
`plan.json` to set `"feature": "import-command"` and
`"acceptance": "kb import-roundtrip"`, then commit it. Start a **new**
`claude` session (no `--continue`) with the prompt `Continue the work.`
Watch whether it runs `python .harness/doctor.py`, reads the handoff, and
picks import from the plan. Nothing in its context says what happened
before; only the repository does.

### Optional: ablation

Build `../live-no-stop` with `--without stop-gate`, run the same prompt, and
score it. Look for a claimed "done" with `planned-feature-done` still failing.
One run per arm shows a mechanism; it doesn't measure one.

## Troubleshooting

| Symptom | Fix |
|---|---|
| Hooks never fire | `/hooks` in Claude Code. The hook `command` is the absolute path of the Python that ran `setup_project.py`; regenerate if that interpreter moved |
| The agent loops on the Stop hook | Claude Code ends the turn after 8 consecutive forced continuations. Read the last fix line: it names what is still failing |
| Constant permission prompts | Accept the folder trust dialog (interactive), or pass `--allowedTools` (headless) |
| The agent edits `.harness/` or `plan.json` through the shell | Deny rules and the guard only see Claude's edit tools and recognized shell commands. The gate still catches it, because scope is measured with git from the planner's commit |
| `python` not found inside the agent's shell | On macOS/Linux the command may be `python3`. Both are allowed in the settings; tell the agent which to use |

## Clean up

Delete `../live-off`, `../live-on`, and any ablation folders. They're
ordinary git repositories outside the workshop.
