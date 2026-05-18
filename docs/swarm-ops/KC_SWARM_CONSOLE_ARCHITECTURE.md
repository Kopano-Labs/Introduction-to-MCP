# KC Swarm Console — architecture (wireframe companion)

**Visual wireframe:** [tools/kc-swarm-console-wireframe.html](./tools/kc-swarm-console-wireframe.html)  
**GUI IA spec (columns, flows, branch protection):** [KC_SWARM_CONSOLE_WIREFRAME_SPEC.md](./KC_SWARM_CONSOLE_WIREFRAME_SPEC.md)  
**Doctrine + proof bar:** [SWARM_OPERATIONS.md](./SWARM_OPERATIONS.md)  
**Git + JSONL mechanics:** [GIT_AND_PROOF_NOTEBOOK.md](./GIT_AND_PROOF_NOTEBOOK.md)

This document captures the **design intent** behind the unified KC Swarm Console: one surface that merges sync awareness, JSONL validation, proof gating, connector registry, skills, swarm dispatch, and a **single central composer** aimed at orchestration behind **`https://context.kopanolabs.com`** (verified HTTP 200; see [VERIFIED_ENDPOINTS.md](./VERIFIED_ENDPOINTS.md)). Legacy hostname `kopanocontext.kopanolabs.com` did **not** resolve on last probe—do not wire new BFF targets to it until DNS is fixed.

> **Verify** product stack claims (Next.js version, CI layout, public APIs) against your own Kopano Context / Studio repositories and runbooks. Marketing pages summarize direction; they are not a substitute for internal specs.

---

## 1. GUI structure

The wireframe keeps the **primary action as one prompt box** so it matches “prompt exactly like now in this context window,” while **Web, Fetch, Git, Swarm, and Proof** appear as secondary chips and actions—not competing centers of attention.

**Regions**

| Region | Role |
|--------|------|
| Left rail | Mode switching (Context, Swarm, Proof, CI) |
| Left sidebar | Connectors, abilities, tool status |
| Main | Session header + optional KPI / sync strip + **composer** |
| Right rail | Implementation notes, CI, proof checklist, receipts |

**Flow (connection model)**

1. Operator prompt enters **KC**.  
2. KC routes to the **`cassey`** persona (and policy) on the **server**.  
3. Optional **swarm** workers fan out for research and validation (external executors).  
4. **Receipts** (URLs, exit codes, SHAs) flow back into **proof state** before the UI may mark work complete.

That keeps connectors, skills, abilities, tools, and swarm **in one workspace** instead of scattering them across separate utilities.

**Product positioning (external)**

The [Kopano Labs](https://kopanolabs.com) site presents Kopano Context as an orchestration layer across products. Treat the console as a **front end to that layer**, not a disconnected toy UI—again, confirm APIs and deployment details in your own docs.

---

## 2. HTTPS and the browser (BFF pattern)

**Do not** connect the browser directly to model providers or to long-lived orchestration secrets.

Google’s learning content for Gemini in the browser emphasizes that **direct web-client access is appropriate for prototyping** and that **production** use should move toward **server-side or otherwise protected** access patterns. See [Getting started with the Gemini API in web apps](https://developers.google.com/learn/pathways/solution-ai-gemini-getting-started-web) (Google Developers).

**Recommended shape**

- The SPA or Studio shell **POST**s to your app, e.g. `POST /api/kc/chat`.  
- A **route handler / BFF** (e.g. Next.js Route Handler or server action) holds **service credentials**, attaches `workspaceId`, `persona: "cassey"`, tool permissions, and proof requirements, then calls **`https://context.kopanolabs.com`** (or the internal gateway in front of it).  
- The handler **streams** the model/tool response back into the same central composer.

That preserves an IDE-like chat feel while keeping **credentials and policy on the server**.

---

## 3. CI proof hook — **this repo vs. optional `proof_gate.py`**

**What exists today in this fork**

Workflow: [`.github/workflows/swarm-proof.yml`](../../.github/workflows/swarm-proof.yml) runs on PRs that touch swarm paths:

```yaml
python scripts/kc_log_append.py validate
python scripts/kc_log_append.py proof-check
```

There is **no** `scripts/proof_gate.py` checked in. Do not document that filename as shipped unless you add it.

**What a future `proof_gate.py` (or extended `proof-check`) could add**

Ideas aligned with [SWARM_OPERATIONS.md](./SWARM_OPERATIONS.md):

- Required files present (e.g. `docs/swarm-ops/SWARM_OPERATIONS.md`).  
- `docs/swarm-ops/logs/KC Main Brain Log.jsonl` and `KC Review Log.jsonl` exist and parse.  
- Rows of kind `swarm_ack` / `kimi_ack` include **`evidence_url`** (or your schema’s equivalent list) where doctrine requires it.  
- Optional: compare advertised SHA to `git rev-parse HEAD` for PRs that claim a specific revision.  
- Reject narrative “swarm complete” without **external** receipts.  
- Flag attempts to treat **gitignored** trees (e.g. local `Schematics/` mirrors) as **committed** proof.

Implement that either by **extending** `kc_log_append.py proof-check` or by adding a small **`proof_gate.py`** invoked from the same workflow—**avoid two conflicting gates** that disagree on rules.

[Kopano Labs](https://kopanolabs.com) describes using automation in delivery; mirror **your** real pipeline (branch filters, path filters, required checks) in GitHub—not the marketing page alone.

---

## 4. Implementation order (restraint)

Build in layers so the product stays simple and does not collapse into an admin maze (compare “focused workspace” product narratives—e.g. [Cursor](https://cursor.com) public positioning on agents and parallel work as **one** coherent environment).

Suggested order:

1. **App shell** — layout from the wireframe; theme; navigation.  
2. **Streamed chat route** + **BFF** to Kopano Context.  
3. **Persona routing** — KC → Cassey.  
4. **Tool adapters** — Web / Fetch / Git (server-side).  
5. **Receipts store** + surfacing **`validate` / `proof-check`** results in the Proof rail.  
6. **Swarm controls** — dispatch, ACK ingestion, JSONL append from server only.

**UX rule:** the **composer stays dominant**; connectors, skills, validator, and proof are **supportive side intelligence**.

---

## 5. One-line synthesis

> **Prompt once → route (local vs swarm) → execute → collect receipts → validate/proof-check → only then “complete.”**

For day-to-day Git + JSONL commands, stay on [GIT_AND_PROOF_NOTEBOOK.md](./GIT_AND_PROOF_NOTEBOOK.md) and [NAVIGATION.md](./NAVIGATION.md).
