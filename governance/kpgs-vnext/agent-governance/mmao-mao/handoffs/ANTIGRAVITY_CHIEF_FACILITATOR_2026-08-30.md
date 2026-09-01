# Anti-Gravity Chief Facilitator Handoff - MMAO + MAO Identity-Governance POC

**From:** Codex / stateless renter executing the bounded repository task
**To:** Anti-Gravity / Chief Facilitator
**Status:** Contract POC prepared; no controlled model/interface run has executed
**Base state inspected:** `RobynAwesome/Introduction-to-MCP` at `551a422ab4f906b815f5cc5fd80a76b9ba9a1e9e`
**Implementation receipt:** `133c7d9f09a35fe30786fc13f80efb337a1e6c0c`

## What was found

- MAO already owns a route/dispatch surface in `Structure/07-Agents/ROLE_BINDINGS.json` and `kopano-core/kopano/mao_dispatch.py`.
- MMAO already has mesh/orchard terminology and historical role records in `Structure/07-Agents/AGENT_MESH.json` and `docs/swarm-ops/RTCP_SPEC.json`.
- `task-contract/`, `evidence/`, `evaluation/`, root `NOW.md`, and `MMAO Session Failures/` are existing canonical governance owners.
- Historical role documents are not silently rewritten by this POC.

## Canonical artifacts added or updated

| Artifact | Result |
|---|---|
| `agent-governance/mmao-mao/README.md` | Additive architecture note, term boundaries, model x interface research surface, RTC/evidence rules |
| `identity-provenance.schema.json` | Identity, seat, interface, model/version, task, scope, authority, context, provenance, and receipts are separate claims |
| `authority-boundary.schema.json` + fixture | High task authority is bounded; the global structural-maintenance allowlist is Codex, Anti-Gravity, Cursor |
| `model-interface-affinity-experiment.schema.json` + fixture | Planned reference/model-only/interface-only/seat-only/substrate comparison matrix |
| `failure-receipt.schema.json` + synthetic fixture | Five Whys, correction, retest, metadata-only traces, independent RTC review semantics |
| `validate.py` + focused test | Dependency-free proof that the fixtures preserve the declared boundaries |
| `specs/mmao-mao-identity-governance-v0.1.json` | Bounded R2 governance build specification |
| root `NOW.md` | Current-state receipt and next admissible action |

## Unresolved questions - retain as explicit unknowns

1. Is **"Recycler MMAO with Plus MAO"** the final canonical spelling, or only the preserved spoken working testimony?
2. Which concrete model version, interface version, task payload, and tool-permission profile should be used for the first live controlled run?
3. Which reviewer seats will produce independent evidence for the first run, and what exact evidence will each inspect?
4. Are any historical RTCP/mesh role records intended to be migrated to the current three-seat structural-maintenance boundary? Do not infer this from the POC.

## Proposed RTC opinions to request

These are review requests, not pre-issued opinions.

| Requested reviewer/seat | Question | Required evidence |
|---|---|---|
| Khelos / validation | Does the run preserve the declared invariant set and classify failure without scope drift? | Exact commit, test output, tool trace metadata, failure receipt |
| KC / observer | Does root `NOW.md` correctly distinguish current contract state from historical role material? | Current root `NOW.md`, source paths, commit receipt |
| Anti-Gravity / facilitation | Is the first live run sufficiently bounded, recoverable, and worth admitting? | Build spec, boundary matrix, planned experiment record, rollback procedure |

No review count can promote a conclusion. Missing or conflicting evidence remains `HOLD`.

## Exact next task to facilitate

Create one **reference run** only from `recycler-mmao-plus-mao-experiment.json`:

1. Pin the exact merged commit and a fresh root `NOW.md` reference.
2. Choose one model version and one interface version; record them before execution.
3. Provide one bounded task with explicit include/exclude paths and no production side effects.
4. Capture only metadata-level tool/action traces plus verifier output.
5. Record the result as `executed`, `held`, or `invalidated`; do not infer affinity from one run.
6. Request the three independent review surfaces above and preserve disagreements.
7. If a failure appears, create a real failure receipt from the schema, apply the correction, and retest under the same invariant set.

Do not start with global GSMB restructuring, broad multi-agent dispatch, provider mutations, or a large model matrix. One controlled reference run is the smallest valid next step.

## Black Beast reconstruction after merge

```powershell
git fetch origin
git switch master
git pull --ff-only origin master
python governance/kpgs-vnext/agent-governance/mmao-mao/validate.py
python governance/kpgs-vnext/validate_contracts.py
pytest -q tests/test_mmao_mao_identity_governance.py
```

If the merge commit is not yet on `master`, check out the reviewed branch/commit explicitly instead. Read root `NOW.md` before any run. A failed check is a `HOLD`, not a reason to recreate the contract from memory.
