# Git integrity + swarm proof — notebook (repo-aligned)

This file mirrors the “notebookLM” outline you drafted, **corrected to this repository**: log paths, subcommands, and filenames match `scripts/kc_log_append.py`, `scripts/git_sync_monitor.py`, and `.github/workflows/swarm-proof.yml`.

| Tag | Meaning |
|-----|---------|
| **Verified Git** | Standard Git behaviour; corroborate with [git-scm.com](https://git-scm.com/docs) and linked tutorials. |
| **Designed (repo)** | This fork’s scripts, JSONL paths under `docs/swarm-ops/logs/`, HTML tools, and CI workflow. |

---

## 1. Audit Git remote config + SHA mapping

### Core commands

```bash
git remote -v
git remote show origin
```

Shows remotes, URLs, and default fetch/push behaviour. Community references: [GeeksforGeeks — git remote](https://www.geeksforgeeks.org/git/handling-repositories-with-git-remote/), [LabEx — verify remote settings](https://labex.io/tutorials/git-how-to-verify-git-remote-settings-425663).

**Fork reality:** `origin` may point at `Kopano-Labs/Introduction-to-MCP` while your personal fork is elsewhere. Use a second remote (e.g. `fork`) or change `origin` before you treat GitHub URLs as proof receipts.

### Local ↔ remote SHA alignment

```bash
git fetch origin
git rev-parse HEAD
git rev-parse origin/main   # or origin/master — match your default branch
```

`git rev-parse` prints the commit object name for a ref. See [Adam Johnson — show/copy SHAs](https://adamj.eu/tech/2022/10/24/git-how-to-show-and-copy-commit-shas/).

### Check if a commit object exists locally

```bash
git cat-file -e <sha>
echo $?    # bash: 0 = exists
```

PowerShell:

```powershell
git cat-file -e <sha>
if ($LASTEXITCODE -ne 0) { Write-Host "missing" }
```

Background: [codegenes — test commit by SHA](https://www.codegenes.net/blog/how-to-check-if-the-commit-exists-in-a-git-repository-by-its-sha-1/).

### Check remote without full fetch

```bash
git ls-remote origin refs/heads/main
git ls-remote origin <full40CharSha>
```

`git ls-remote` answers whether a ref or object name exists on the remote without merging it into your worktree. Short SHAs are ambiguous; prefer the full 40-character hash when probing remotes.

### Diagnose divergence

```bash
git log --oneline HEAD..origin/main
git log --oneline origin/main..HEAD
```

---

## 2. Git Sync Monitor (this repo)

| Surface | Path | Role |
|--------|------|------|
| Live diagnostics | `scripts/git_sync_monitor.py` | Remotes, upstream, ahead/behind, `Schematics/` ignore vs tracked, `--strict-unpushed` |
| Static dashboard | [tools/git-sync-monitor.html](./tools/git-sync-monitor.html) | Open in browser; copy-paste blocks + proof checklist |
| URL templates | `scripts/swarm_remote_proof_urls.sh`, `scripts/swarm_remote_proof_urls.ps1` | Compare / commit / Actions URLs from remote |

Run:

```bash
python scripts/git_sync_monitor.py
python scripts/git_sync_monitor.py --strict-unpushed   # exit 1 if unpushed vs @{upstream}
```

The bash “v1 concept” loop you sketched is still valid; the Python script is the maintained implementation so Windows and error handling stay consistent.

### Optional: minimal bash probe (portable v0)

Use when you want a shell-only snapshot (Linux/macOS/Git Bash). Replace `origin/main` with `origin/master` if that is your default branch.

```bash
#!/usr/bin/env bash
set -euo pipefail
echo "=== REMOTE CHECK ==="
git remote -v || echo "No remote configured"

echo "=== BRANCH STATUS ==="
git status -sb

echo "=== UPSTREAM CHECK ==="
git rev-parse --abbrev-ref --symbolic-full-name '@{u}' 2>/dev/null \
  || echo "No upstream tracking branch"

echo "=== DIVERGENCE (after fetch) ==="
git fetch origin >/dev/null 2>&1 || true
git log --oneline "HEAD..origin/main" 2>/dev/null | wc -l | xargs echo "Commits behind (origin/main):"
git log --oneline "origin/main..HEAD" 2>/dev/null | wc -l | xargs echo "Commits ahead (origin/main):"

echo "=== IGNORE CHECK (Schematics) ==="
git check-ignore -v Schematics/ 2>/dev/null || echo "Not ignored (or path missing)"
```

For ignored paths as a listing, `git status --ignored` is useful but noisy; see [git-status](https://git-scm.com/docs/git-status) and practical notes e.g. [SQLPey — ignored files](https://sqlpey.com/git/effective-git-commands-to-list-files-ignored-by-gitignore/).

---

## 3. Verify `Schematics/` is ignored

### Direct rule

```bash
git check-ignore -v Schematics/
```

Official docs: [git-check-ignore](https://git-scm.com/docs/git-check-ignore).

### List ignored paths (can be noisy)

```bash
git ls-files --others --ignored --exclude-standard
```

`git status --ignored` (optionally with `-u` for untracked) also surfaces ignored entries; output format varies by Git version—prefer `git check-ignore -v` for a definitive rule line.

See also [Andrii Khorodnyk — list ignored files](https://aohorodnyk.com/post/2023-11-28-list-all-ignored-files-in-git/).

**Important:** A path can be listed in `.gitignore` but still **tracked** if it was committed before the ignore rule. Use `git ls-files Schematics` and `git check-ignore -v` together.

---

## 4. Trace a “missing” commit (fork / local)

1. Search history: `git log --all --oneline --grep "<keyword>"`
2. Reflog: `git reflog` — [GeeksforGeeks — recovering commits](https://www.geeksforgeeks.org/git/recovering-lost-commits-in-git/)
3. Recover on a branch: `git switch -c recovery <sha>`
4. Dangling objects: `git fsck --lost-found` — e.g. [GAT docs](https://gat.sh/docs/find)
5. On remote: `git ls-remote origin <sha>`

---

## 5. What changed vs upstream fork

There is no public substitute for **your** `git log`; sources cannot print your fork diff. Locally:

```bash
git remote add upstream https://github.com/Kopano-Labs/Introduction-to-MCP.git   # once
git fetch upstream
git log --oneline upstream/main..HEAD
git log --oneline HEAD..upstream/main
git log --graph --oneline --all --decorate -20
git diff upstream/main...HEAD
```

---

## 6. Validator + proof check (integrated **in this repo**)

There is **no** `scripts/kc_log_validate.py`. Validation and proof gates live on **`scripts/kc_log_append.py`** as **subcommands** (two separate invocations, not one compound flag):

```bash
python scripts/kc_log_append.py validate
python scripts/kc_log_append.py proof-check
```

Chained (fail fast):

```bash
python scripts/kc_log_append.py validate && python scripts/kc_log_append.py proof-check
```

**Unified wrapper (this repo):** `python scripts/kc_guard.py all` runs `git_sync_monitor.py` (plus required-file presence), then `validate`, then `proof-check`, then **doc host drift** (dead/unlisted `kopanolabs.com` URLs in swarm-ops docs; skip with `--no-check-doc-hosts`). Optional: `all --require-swarm-ack` after a real `kimi_ack` or `swarm_ack` row with `evidence_urls`. See [KIMI_ACK_FORMAT.md](./KIMI_ACK_FORMAT.md) and [KC_SWARM_CONSOLE_WIREFRAME_SPEC.md](./KC_SWARM_CONSOLE_WIREFRAME_SPEC.md).

**Not supported:** `python scripts/kc_log_append.py --strict-proof --validate` — `--strict-proof` is an **append** flag on `review` / `mainbrain` / `kimi-ack`, not a global paired with `validate`. Use **`kc_guard.py`** for a single orchestrated entrypoint; add a heavier `kc_swarm_doctor.py` later only if you need extra diagnostics.

- **`validate`** — schema check on JSONL lines (default paths under `docs/swarm-ops/logs/`).
- **`proof-check`** — requires a recent student/audit row in **KC Review Log** and a non-bootstrap receipt in **KC Main Brain Log**, each with `exit_code` and `evidence_urls`.

Append commands (each is its own invocation):

```bash
python scripts/kc_log_append.py review --role student --phase audit --summary "..." \
  --commands pytest tests/test_kc_log_append.py --exit-code 0 \
  --evidence-url "https://..." --strict-proof

python scripts/kc_log_append.py mainbrain --kind swarm_ack --summary "..." \
  --exit-code 0 --evidence-url "https://..." --strict-proof

python scripts/kc_log_append.py kimi-ack \
  --payload-ref docs/swarm-ops/PAYLOAD_KIMI_300_ACTIVATION.md \
  --status acknowledged --notes "..." --exit-code 0 \
  --evidence-url "https://..." --strict-proof
```

**`--strict-proof`** (where supported): enforces exit code + at least one evidence URL on append; may **warn** if `git_sha` is missing rather than hard-failing — see argparse help on each subcommand.

**`--teacher-verdict`** on `review` is only `approved` or `rejected` (not `pass`).

---

## 7. CI hook (already present)

Workflow: [.github/workflows/swarm-proof.yml](../../.github/workflows/swarm-proof.yml)

On pull requests to `main` / `master` that touch swarm paths, it runs:

```yaml
python scripts/kc_log_append.py validate
python scripts/kc_log_append.py proof-check
python scripts/kc_guard.py all
```

There is **no** `kc_log_validate.py` in this tree. **`kc_guard.py`** delegates to `git_sync_monitor.py` and the two `kc_log_append` steps above (single entrypoint for operators and CI).

**You may need to extend `branches:` or add path filters** if you merge from `codex/*` or other long-lived branches.

---

## 8. ACK capture → logs

Canonical payload: [PAYLOAD_KIMI_300_ACTIVATION.md](./PAYLOAD_KIMI_300_ACTIVATION.md).  
ACK format notes: [KIMI_ACK_FORMAT.md](./KIMI_ACK_FORMAT.md).

**Preferred machine row for Kimi acknowledgement:** `kimi-ack` (writes structured `kimi_ack` block).  
**Alternative:** `mainbrain --kind swarm_ack` if you want a free-form orchestrator row.

Rule (doctrine): **no “swarm complete” without durable external evidence** — see [SWARM_OPERATIONS.md](./SWARM_OPERATIONS.md).

---

## 9. GUI / MCP / Kopano vision (architecture only)

Layers you described map cleanly to:

| Layer | Responsibility |
|-------|------------------|
| **UI** | Prompt surface, agent picker (KC ↔ Cassey ↔ swarm), transcript |
| **MCP / tools** | Git, logs append/validate, browser/search, connectors |
| **Swarm** | External executor (e.g. Kimi); payload dispatch; ACK back |
| **Logging** | JSONL append + `validate` / `proof-check` + optional CI |

UX principle: **prompt → route (local vs swarm) → execute → ACK → append logs → proof gate.**

Implementing “Perplexity-class web depth” requires a **backend retrieval path** (search API, MCP fetch, or RAG), not UI copy alone. Studio API base configuration lives under `kopano-core/studio/` (see `VITE_KC_API_BASE_URL` in repo).

---

## 10. One-line synthesis

> Git integrity (remotes, SHAs, ignore rules) and swarm proof (JSONL + external URLs + CI) are one governed system: **no completion claim without receipts.**

---

## Next steps (pick one)

1. **Stricter CI** — add `python scripts/kc_guard.py all --require-swarm-ack` to the workflow once every PR that touches swarm logs must include a real `swarm_ack` + evidence URLs (will fail until logs contain that row).
2. **Studio shell** — implement the Next.js / BFF chat route described in [KC_SWARM_CONSOLE_ARCHITECTURE.md](./KC_SWARM_CONSOLE_ARCHITECTURE.md); wire Proof rail to `kc_guard` or in-app calls to the same checks.

**Done in-repo:** unified CLI = **`scripts/kc_guard.py`**; GUI IA = [KC_SWARM_CONSOLE_WIREFRAME_SPEC.md](./KC_SWARM_CONSOLE_WIREFRAME_SPEC.md) + [tools/kc-swarm-console-wireframe.html](./tools/kc-swarm-console-wireframe.html).

Otherwise this notebook + [NAVIGATION.md](./NAVIGATION.md) is the durable index.
