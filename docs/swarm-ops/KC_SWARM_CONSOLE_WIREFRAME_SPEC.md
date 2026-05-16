# KC Swarm Console — GUI wireframe layout spec

**Visual mock:** [tools/kc-swarm-console-wireframe.html](./tools/kc-swarm-console-wireframe.html)  
**Architecture (BFF, CI alignment):** [KC_SWARM_CONSOLE_ARCHITECTURE.md](./KC_SWARM_CONSOLE_ARCHITECTURE.md)  
**Unified CLI:** `python scripts/kc_guard.py all` — see [GIT_AND_PROOF_NOTEBOOK.md](./GIT_AND_PROOF_NOTEBOOK.md)

This is an **IA + interaction spec** for engineers (not production code). Goal: **Cursor / Gemini / Codex-style** simplicity — **one dominant prompt**, side intelligence for tools, proof, and swarm.

---

## Global layout (four columns; collapse on narrow viewports)

| # | Region | Contents |
|---|--------|----------|
| 1 | **Left rail** (icon-only) | Console (chat), Swarm, Proof, CI, Settings |
| 2 | **Left sidebar** | Workspace selector (e.g. Main Brain); persona router **KC → Cassey**; connectors (Web, GitHub, Kopano Context, JSONL ledger); skill toggles (teacher depth, strict proof, swarm fan-out) |
| 3 | **Center (primary)** | Single transcript; **one composer**; tool chips: **Web / Fetch / Git / Swarm / Proof**; attachments strip for receipts + log refs |
| 4 | **Right rail** | **Receipts & proof bar** (live checklist); **Git sync health** (remote, branch, ahead/behind); **Logs** (latest JSONL + validate status); **CI** (workflow run deep link) |

Responsive: ≤1320px hide right rail into drawer; ≤980px rail + sidebar collapse to hamburger — same pattern as [kc-swarm-console-wireframe.html](./tools/kc-swarm-console-wireframe.html).

---

## Core flows

### A) Prompt → route → execute

1. Operator types in the composer.  
2. Persona: KC default; **Cassey** for teacher / student depth.  
3. Tool chips select server-side capabilities (never raw keys in browser — see architecture doc).

### B) Swarm dispatch

- **Swarm** opens a compact plan drawer: workers (research / verify / patch / summarize); **receipts required** ON by default.  
- Results stream into the transcript as **worker cards** with links for the proof bar.

### C) Proof gate (UI)

- **Mark complete** disabled until doctrine satisfied (mirror `kc_log_append.py proof-check` + optional `--require-swarm-ack`).  
- On pass, show **Proof bar: PASS** with SHA + evidence URLs surfaced.

---

## UX rules (non-negotiable)

- **One dominant composer** — no competing “dashboard home.”  
- Proof is **visible but quiet** until something fails (then actionable: “missing `evidence_urls`” → button to open append helper / copy CLI).  
- Failures are **actionable** with a path to `kc_guard` / `kc_log_append` commands.

---

## Git primitives (operator reference)

These are standard Git behaviours (not M365 or internal search):

- Ignore rules: [`git check-ignore`](https://git-scm.com/docs/git-check-ignore)  
- Remotes: [GeeksforGeeks — git remote](https://www.geeksforgeeks.org/git/handling-repositories-with-git-remote/)  
- Commit exists locally: [`git cat-file -e`](https://www.codegenes.net/blog/how-to-check-if-the-commit-exists-in-a-git-repository-by-its-sha-1/)  
- Current SHA: [Adam Johnson — rev-parse / copy SHA](https://adamj.eu/tech/2022/10/24/git-how-to-show-and-copy-commit-shas/)  
- Ignored file listing: [`git status --ignored`](https://git-scm.com/docs/git-status), [SQLPey](https://sqlpey.com/git/effective-git-commands-to-list-files-ignored-by-gitignore/), [Khorodnyk](https://aohorodnyk.com/post/2023-11-28-list-all-ignored-files-in-git/)

---

## CI + branch protection (structural enforcement)

**In-repo:** [.github/workflows/swarm-proof.yml](../../.github/workflows/swarm-proof.yml) runs `kc_log_append.py validate`, `proof-check`, and **`kc_guard.py all`**.

**On GitHub (manual):** Settings → Branches → add rule for `main` / `master`:

- Require status check **Swarm proof gate / swarm-jsonl** (name matches the workflow job).  
- Optionally “require branches up to date before merging.”

**Stricter doctrine (optional PRs only):** if a PR claims swarm completion, add a workflow job or local convention:

```bash
python scripts/kc_guard.py all --require-swarm-ack --strict-unpushed
```

`--require-swarm-ack` is **off** in the default workflow so fresh clones with only `obedience` placeholder rows still pass until you intentionally tighten the bar.

---

## Scoped proof (optional)

If you do not want every PR to require `swarm_ack`, gate on changed files:

```bash
git diff --name-only origin/main...HEAD
```

Then run `kc_guard.py validate` always, and `all --require-swarm-ack` only when `docs/swarm-ops/logs/` or swarm payload paths change.
