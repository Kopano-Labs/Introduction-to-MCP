# LEFA-AI Featherless Auth + Over-Explanation — Case 002

> **Actor:** Copilot CLI (stateless renter)
> **Date:** 2026-09-02 SAST
> **Repo:** `RobynAwesome/lefa-ai` — branch `robynawesome-fix-backend-seed`
> **Fix commit:** `8acd8f9d0a01b47a499794b4fa1c2a919d9d1370`
> **Constraint:** `I_AM_STATELESS_RENTER_NOT_LANDLORD`

## Failure studied

Latent, not a crash — baseline `pytest tests/ -q` was 57/57 PASS.

1. **Placeholder credential shipped as if real.** `src/lefa/featherless.py` sent `Authorization: ******` literally. Every live Featherless inference call was unauthenticated by construction and silently fell back offline. NOW.md carried `POC_VALIDATED` for Featherless while the runtime path could not authenticate. `MODEL MEMORY != GROUND TRUTH`.
2. **Over-explaining fallback.** On any provider error the user was shown `LEFA Governed Companion: ... [Inference offline fallback: HTTP_403]` — internal debug detail on a non-technical user's face. Violates the Heavy Backend / Easy Immersive Interface law.

## Invariant

```text
RECEIPT OR HOLD — a placeholder is not a credential.
CURRENT / REALITY STATE > INDEX STATE — green tests did not prove live auth.
EASY INTERFACE — failure detail lives in logs, never in the user's narrative.
```

## Transition

| Defect | Before | After |
|---|---|---|
| Auth header | `Authorization: ******` | `Authorization: Bearer {self.api_key}` |
| Fallback | self-referential + `[Inference offline fallback: HTTP_403]` | `Observation recorded under governed deterministic policy.` (reason -> server log) |
| Signature | `_fallback_explanation(messages, reason)` | `_fallback_explanation(reason)` (dead param removed) |
| Test | pinned debug text as user-visible | pins calm line, asserts `HTTP_403` absent |

## Receipt

- `pytest tests/ -q` -> 57/57 PASS after change (exit 0).
- No execution authority added; observation/paper boundary untouched.

## Hold (not promoted)

- Default API key literal remains in source; rotation is a separate admissible action.
- Live Featherless round-trip not witnessed from this environment; auth fix is structural. Live POC promotion requires a witnessed HTTP 200 receipt.

`FAILURE_SEED_STUDIED -> FIXED -> RECEIPTED`