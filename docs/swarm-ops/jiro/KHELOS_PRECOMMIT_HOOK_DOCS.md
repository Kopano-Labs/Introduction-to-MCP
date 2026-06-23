# KHELOS Pre-Commit Hook Documentation

> `hooks/pre-commit-kpgs-gate.py` — Governance vault protection in code.

## What It Does

Blocks commits that modify governance vault files without a valid session receipt.

## Protected Paths (Require Session Receipt)

- `Schematics/18-PROTOCOLS/`
- `Schematics/00-Home/Dashboard.md`
- `Schematics/index.md`
- `Schematics/CLAUDE.md`
- `Schematics/21-KOPANO-PHU GOVERNACE SYSTEMS/MAIN-BRAIN/`
- `Schematics/KVC_Main_Brain_Index.md`

## Allowed Paths (No Gate Required)

- `scripts/`
- `poc-vs-foc/`
- `hooks/`
- `Schematics/11-AI HALLUCINATION - CRITICAL/` (incident logging always allowed)
- Any `README.md`
- `.gitignore`

## How It Works

1. On `git commit`, hook checks staged files
2. Classifies each file as GOVERNANCE or ALLOWED
3. If GOVERNANCE files staged → checks for session receipt in `poc-vs-foc/`
4. Receipt must be from TODAY (ISO date match)
5. If no receipt → COMMIT BLOCKED with clear error message
6. If receipt exists → commit proceeds

## Installation

```bash
cp hooks/pre-commit-kpgs-gate.py .git/hooks/pre-commit
```

## Receipt Format

Any JSON file in `poc-vs-foc/` matching `*_RECEIPT.json` or `*_CLOSE.json` with today's date in `timestamp` field.

## Bypass (NEVER DO THIS)

```bash
git commit --no-verify  # VIOLATES KPGS LAW
```

Using `--no-verify` is logged as insubordination if discovered.

## Why This Exists

Session 1: Jiro (Kiro) created 8 files in governance vault without reading the GSMB. KHELOS said: "Text does not stop machines. Code stops machines." This hook IS that code.

**Jesus is King. The gate is locked.**
