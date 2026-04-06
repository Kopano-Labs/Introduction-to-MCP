# Orch User Guide (PowerShell)

## 1) First-time setup

From repo root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
```

If `orch` is still not recognized, use:

```powershell
python -m orch --help
```

## 2) Why `orch` was not recognized

`orch` is a console script created during package install.  
If you activate `.venv` but do not run `pip install -e .`, the command will not exist.

Check command resolution:

```powershell
Get-Command orch -ErrorAction SilentlyContinue
```

## 3) Common PowerShell mistake shown in your session

This fails:

```powershell
`cli.py`
```

That is treated as a command name, not a filename preview.  
Use one of these:

```powershell
Get-Content .\orch\orch\cli.py
notepad .\orch\orch\cli.py
code .\orch\orch\cli.py
```

## 4) Register, login, and admin bootstrap

Register:

```powershell
orch user register --email "rkholofelo@gmail.com" --password "ChangeMeNow!" --name "Rkholofelo"
```

Login test:

```powershell
orch user login --email "rkholofelo@gmail.com" --password "ChangeMeNow!"
```

Grant admin + god mode:

```powershell
orch admin grant --email "rkholofelo@gmail.com" --god-mode
```

## 5) Run Orch anytime

CLI:

```powershell
orch --help
orch agents list
orch serve api --host 127.0.0.1 --port 8000
```

Demo-day preflight:

```powershell
.\scripts\demo_day_preflight.ps1
```

Optional readiness and smoke checks:

```powershell
python .\scripts\demo_day_readiness.py --quick
python .\scripts\demo_day_smoke.py --strict
.\scripts\demo_day_launch.ps1
```

API endpoints:

- `POST /auth/register`
- `POST /auth/login`
- `GET /sessions`
- `GET /sessions/{id}`

Open:

```text
http://127.0.0.1:8000
```

## 6) Demo day flow

Canonical runbook:

- `DEMO_DAY_RUNBOOK.md`
- `DEMO_DAY_10_PHASES_50_TASKS.md`
