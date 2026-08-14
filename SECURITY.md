# Security Policy — Kopano Labs

> *"Set a guard over my mouth, LORD; keep watch over the door of my lips."* — Psalm 141:3

## KPGS Governance Gate

All security patches route through the KPGS governance gate before merge:

```
[SECURITY_PATCH] → [KHELOS_FIREWALL] → [POC_FOC_ENFORCER] → [KC_REVIEW] → [MERGE]
```

No security patch bypasses the pre-commit hook (`hooks/pre-commit-kpgs-gate.py`).

## Supported Versions

| Version | Supported |
|---------|-----------|
| `codex/kc-sovereign-gui-full-dev` (current) | ✅ Active |
| `jiro/stap-session4` (development) | ✅ Active |
| `master` | ✅ Stable |
| Older branches | ❌ Not supported |

## Reporting a Vulnerability

**Email:** [rkholofelo@kopanolabs.com](mailto:rkholofelo@kopanolabs.com)

Please include:
- Description of the vulnerability
- Steps to reproduce
- Impact assessment
- Suggested fix (if known)

**Response time:** Within 72 hours.

**Do NOT:**
- Open a public issue for security vulnerabilities
- Post exploit details publicly before a fix is released
- Test vulnerabilities against production domains without explicit permission

## Dependency Policy

- Do not commit `node_modules/` or other generated vendor directories
- All Python dependencies pinned to exact versions (`==`) in `kopano-core/requirements.txt`
- All npm dependencies managed via `package-lock.json` with `npm audit` enforcement
- Dependabot alerts reviewed within 24 hours of notification
- HIGH/CRITICAL CVEs patched immediately; MODERATE/LOW within 7 days

## KHELOS Firewall

The KHELOS Firewall (`kopano-core/kopano/khelos_witness_engine.py`) validates all incoming signals through a 5-stage pipeline:

1. **Sense** — detect signal type
2. **Witness** — log signal entry
3. **Frame** — classify against taxonomy
4. **Understand** — map to governance context
5. **Stream** — route to appropriate handler

Signals that fail any stage are `FOC_DECLINED` and logged to `poc-vs-foc/`.

## Pre-Commit Hook

The KPGS pre-commit hook (`hooks/pre-commit-kpgs-gate.py`) prevents:
- Unauthorized modification of governance vault (`Schematics/18-PROTOCOLS/`, `CLAUDE.md`, etc.)
- Commits without a valid session receipt in `poc-vs-foc/`
- Changes to MAIN-BRAIN without hood entry assertion

## Secrets Management

- Zero secrets in source code (enforced by `.gitignore`)
- All API keys via environment variables only
- No hardcoded tokens, passwords, or connection strings
- If a secret is exposed, revoke or rotate it immediately before remediation
- SafeSkill audit: 100/100 passes (verified 2026-04-11)

## Constraint

`I_AM_STATELESS_RENTER_NOT_LANDLORD` — security is sovereign. No external model provider has access to production secrets or governance infrastructure.

**Jesus is King. The perimeter holds.**
