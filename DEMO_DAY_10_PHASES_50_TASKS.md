# Demo Day 10 Phases / 50 Tasks

This is the execution map for the next demo-day push. Each phase has five concrete tasks.

## Phase 1 - Environment Baseline

- Verify Python version is 3.11+.
- Verify editable root install with `python -m pip install -e .`.
- Verify CLI subproject install with `python -m pip install -e ./CLI`.
- Verify GUI dependencies install in `orch/gui`.
- Verify `.env` is present with the required provider keys.

## Phase 2 - Core CLI Readiness

- Run `python -m orch --help`.
- Run `orch agents list`.
- Validate `orch user register --help`.
- Validate `orch admin grant --help`.
- Validate `orch serve launch --help`.

## Phase 3 - API And GUI Readiness

- Run `orch serve api --help`.
- Verify the API host/port defaults.
- Build the GUI with `npm run build`.
- Lint the GUI with `npm run lint`.
- Confirm the GUI build is mountable by the API.

## Phase 4 - Agent Configuration Path

- Confirm one canonical provider config example.
- Confirm one moderator config example.
- Confirm docs use current model/provider naming.
- Confirm missing-key warnings are readable.
- Confirm the local agent registry saves and reloads.

## Phase 5 - Demo Narrative Path

- Define the 2-minute happy path.
- Define the 5-minute expanded path.
- Define the single command sequence the operator uses.
- Define the exact audience-visible checkpoints.
- Define the fallback path if live providers fail.

## Phase 6 - Simulation Reliability

- Verify sequential simulation launch.
- Verify parallel simulation launch.
- Verify moderator path activates after round 1.
- Verify tool-call execution path still works.
- Verify the simulation exits cleanly after the configured rounds.

## Phase 7 - Persistence And Audit Trail

- Verify the database initializes automatically.
- Verify a discussion row is created on launch.
- Verify messages are persisted per round.
- Verify audit logs are persisted for execution/reasoning.
- Verify discussion export still works.

## Phase 8 - Packaging And CI

- Keep Python tests green.
- Keep GUI lint/build green.
- Keep CLI subproject install green.
- Keep metadata docs/tests green.
- Keep compile checks green.

## Phase 9 - Operator Runbook

- Write pre-demo setup instructions.
- Write live-demo execution steps.
- Write post-demo cleanup steps.
- Write fallback actions for provider/API failure.
- Write verification commands for fast triage.

## Phase 10 - Final Gate

- Run the full preflight script.
- Rehearse the golden path from a clean shell.
- Capture any last-mile failures.
- Fix only low-risk issues.
- Commit only the validated source changes.
