---
title: Swarm Ops & Proof Doctrine
status: canonical
tags: [swarm, kimi, proof, protocol-13, handoff, kopano-labs]
---

# Swarm Ops & Proof Doctrine

**Org context:** [kopanolabs.com](https://kopanolabs.com)

**Repo copy (this path):** version-controlled doctrine and JSONL append targets live under `docs/swarm-ops/`. If you use Obsidian under `Schematics/`, mirror or link these files there so wikilinks resolve in-vault.

This standard governs how multi-agent and high-fanout work is **scoped**, **handed off**, and **verified** for Kopano Main Brain and adjacent repos. It is written for **operators, leads, and audit readers**: repeatable criteria replace informal narrative (“swarm complete”, “all triggers fired”) so claims remain defensible under investor or client scrutiny.

## Swarm operations & platform boundaries

### Kimi vs Cursor — separation of concerns

| Surface | Role |
|---------|------|
| **Kimi / multi-agent swarm** | **External** orchestration runner (platform, job queue, or ops environment). Work products, logs, and artifacts exist **outside** any single IDE workspace. |
| **Cursor (IDE agent)** | **Local** assistant on a checked-out tree: edits, reviews, and **locally invoked** commands under the developer’s control. |

**Non-negotiable boundary:** Cursor in a given workspace does **not** start, host, or attest to a Kimi swarm run. **“Swarm complete”** is satisfied only with **external-runner receipts** that meet the proof bar below—IDE chat transcripts, summaries, or assistant assertions **alone** are insufficient.

### Protocol 13 & honest handoff

- **Protocol 13 — audit-before-presentation:** No client-facing, investor-facing, or “demo-ready” claim without a **verification / red-team pass** on the actual surface (including negative paths: empty states, wrong season, mobile, offline or degraded modes where applicable).
- **Honest handoff:** **Main Brain** must receive receipts (**comms-log**, session notes, execution logs) **before** presentation—not as a retrospective patch after a failed demo.

These intent locks are illustrated by **May 2026** swarm incidents (fixtures / narrative drift class) logged in your vault comms ledger when mirrored.

## Proof bar (required artifacts)

A milestone or deliverable is **accepted** only when applicable rows below are filled with **primary** evidence. **Chat-only proofs are excluded:** model prose, screenshots of chat without CLI/CI/API receipts, or undocumented “green” claims do **not** count toward the bar.

| Commands / jobs | Exit / HTTP | Logs / CI URL | Git SHA | Prod probes |
|-----------------|-------------|---------------|---------|-------------|
| Exact command lines, CI job names, or HTTP endpoints exercised (copy-pasteable). | Exit codes, aggregated test results, or response status lines—not paraphrased success. | Timestamped log excerpts, saved log paths, or **shareable** CI/deployment run URLs. | Branch name and commit SHA (or immutable tag) the evidence was produced against. | For user-facing or production claims: probes against **production or designated staging**, not localhost-only. |

**Classification:** Until the proof bar is met, status is **unknown / not verified**—regardless of internal optimism or swarm scale.

### Automated verification (repo tooling)

The append-only JSONL logs under `docs/swarm-ops/logs/` can be checked locally without relying on human discipline alone:

| Command | Purpose |
|---------|---------|
| `python scripts/kc_log_append.py validate` | Structural validation (unknown keys, required shapes, ISO `ts` prefix). |
| `python scripts/kc_log_append.py proof-check` | `validate` plus **gates**: last `role=student` + `phase=audit` row must include `exit_code` and non-empty `evidence_urls`; last non-`bootstrap` Main Brain row must also carry `exit_code` + `evidence_urls`. |
| `--strict-proof` on `review` / `mainbrain` / `kimi-ack` | Fail the append if `exit_code` or evidence URLs are missing (warns when `git_sha` absent). |

Standard external paste-back for Kimi: [KIMI_ACK_FORMAT.md](./KIMI_ACK_FORMAT.md) and `python scripts/kc_log_append.py kimi-ack …`.

**Cross-links (receipts & precedent):**

- [Kimi 300 activation payload](./PAYLOAD_KIMI_300_ACTIVATION.md) (paste into Kimi; manual execution)
- [KC JSONL logs — schema & CLI](./logs/README.md)

## Handoff envelope (copy-paste template)

Use for swarm → lead → Cursor (or inverse) transitions. Attach files or links; do not substitute narrative for the proof table.

```markdown
## Scope
- Repo:
- Branch / SHA:
- User-visible URL(s) (if any):

## Claims (bullet, testable)
-

## Proof (attach or link — required)
| Claim | Commands / job | Exit / HTTP | Logs / CI URL | Git SHA | Prod probes | Notes |
|-------|----------------|-------------|---------------|---------|-------------|-------|
|       |                |             |               |         |             |       |

## Failures / open risks
-

## Red-team / Protocol 13
- [ ] Audit-before-presentation satisfied for this surface
- [ ] Prod or staging probes attached where the claim is user-visible
- [ ] No acceptance on chat-only “proof”

## Main Brain
- Receipts seeded: yes / no — path(s):

## Sign-off
- Name / role:
- Timestamp (TZ):
```

## Manual initiation payloads (ISIS / Kimi)

Directives intended for paste into **Kimi** (or another external swarm UI) are **vaulted** in-repo at [PAYLOAD_KIMI_300_ACTIVATION.md](./PAYLOAD_KIMI_300_ACTIVATION.md). Cursor does **not** invoke Kimi.

After Kimi acknowledges or produces work products, **seed execution logs** that satisfy the **Proof bar** into your Obsidian **comms-log** (and append machine lines to **`docs/swarm-ops/logs/KC Main Brain Log.jsonl`** via `python scripts/kc_log_append.py mainbrain …` from repo root). Student/teacher audits go to **`docs/swarm-ops/logs/KC Review Log.jsonl`** (`kc_log_append.py review`). Until receipts land, swarm status stays **manual-execution-required** / unverified regardless of rhetoric.

## Non-goals

- Credentializing swarm **headcount** (“300 agents”) — **outcomes and receipts** matter.
- Treating marketing or positioning copy as a substitute for the proof bar.
