# Demo Day Runbook

## Goal

Deliver one clean end-to-end demo using the main `python main.py` surface:

1. configure agents,
2. start the API/GUI,
3. launch a discussion,
4. show live updates in the browser,
5. fall back cleanly if a live provider is unavailable.

## Supported Surfaces

- Main framework: `python -m pip install -e .`
- Separate MCP CLI app: `python -m pip install -e ./CLI`
- GUI workspace: `kopano-core/studio`

## Pre-Demo Checks

Run:

```powershell
.\scripts\demo_day_preflight.ps1
```

Expected outcomes:

- Python tests pass
- root install succeeds
- CLI subproject install succeeds
- `python main.py --help` works
- GUI lint/build passes

Optional fast checks:

```powershell
python .\scripts\demo_day_readiness.py --quick
python .\scripts\demo_day_smoke.py --strict
```

## Golden Path

### 1. Configure agents

```powershell
python main.py agents config gemini-pro --provider google --model gemini-1.5-pro
python main.py agents config grok-mod --provider xai --model grok-beta
python main.py agents list
```

### 2. Start API and GUI

```powershell
.\scripts\demo_day_launch.ps1
```

Open:

```text
http://127.0.0.1:8000
```

### 3. Launch discussion in a second shell

```powershell
python main.py serve launch --topic "The future of AI in South African fintech" --agents "gemini-pro" --moderator "grok-mod" --max-rounds 4 --parallel
```

### 4. Show the audience

- live response updates in the GUI
- moderator guidance between rounds
- persisted sessions and discussion history

## Fallbacks

### If provider auth fails

- use the local CLI/API help flow as the backup demo
- show agent config, session surfaces, and Labs UI without promising live model responses

### If GUI does not load

- keep the API shell running
- show persisted sessions with:

```powershell
python main.py log list
python main.py log view 1
```

### If the console script is not on PATH

Use:

```powershell
python main.py --help
```

## Fast Triage

```powershell
python -m pip install -e .
python -m pip install -e ./CLI
python .\scripts\demo_day_readiness.py --quick
cd kopano-core\studio; npm run lint; npm run build
```
