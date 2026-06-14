# Teacher–Student Apprenticeship Protocol (TSAP)

**Bracket tag:** `[TSAP_PROTOCOL]`  
**Copy lane:** KC — Cassey whole training (teacher) · Cassy lead student · KC brain ledger  
**Ecosystem:** Kopano-Phu Eco-Friendly System — **Kopano Labs** (Experimentation) × **Ama-Phu Entertainment** (Creativity) as one.

## Bracket syntax (every receipt)

Use brackets deliberately — each token is machine-parseable:

```
[TSAP_PROTOCOL] timestamp: 2026-05-31T20:00:00Z | lane: mcp | role: teacher | department: kopano_labs_experimentation | student: cassy | verdict: APPROVE
```

```
[TSAP_PROTOCOL] timestamp: … | lane: mao | role: student | department: ama_phu_creativity | agent: pipeline_drone | action: audit | verdict: SUBMITTED
```

```
[BLACK_MASK_DRILL] timestamp: … | agent: mirror_warden | commandments_pass: 15/15 | pillars_pass: 5/5 | verdict: SHIP
```

Relation to [BRACKET_PROTOCOL](../BRACKET_PROTOCOL.md): Bracket Protocol is the **breaking point** for Main Brain + sub-brain attach. TSAP is the **teacher–student loop** inside that ecosystem.

## Dual teaching surfaces

| Surface | Teacher agent | Student agent | Job |
|---------|---------------|---------------|-----|
| **MCP (TSAP server)** | `mcp_teacher` → Cassey lane | `mcp_student` → Cassy lane | Tool-first apprenticeship, Review Log, BlackMask drill |
| **MAO (orchestrator)** | `mao_teacher` → Operational General + Cassey | `mao_student` → Cassy + department students | Route + execute bounded turns per department |

Both surfaces teach the **same** ecosystem agents. Category = department parent (`kopano_labs` | `ama_phu`).

## Teacher–student loop (copy KC / Cassey training)

1. **Student action** — agent proposes change, runs tests, captures evidence.
2. **Student audit** — append `docs/swarm-ops/logs/KC Review Log.jsonl` via `kc_log_append.py review`.
3. **Teacher review** — MCP `tsap_teacher_review` or MAO `mao_tsap_teacher_turn`.
4. **Approval** — seed Main Brain / department receipt; append `[TSAP_PROTOCOL]` with `verdict: APPROVE`.
5. **Rejection** — `verdict: RETRY`; failure logged for Chief Architect.

## Black Mask testing (NB)

Before any agent operates in a department, run **Black Mask drill**:

- All **15 Commandments** — see [BLACK_MASK_COMMANDMENTS.json](../BLACK_MASK_COMMANDMENTS.json)
- All **5 Pillars** — Grit, Realism, Aesthetics, Sovereignty, Apprenticeship

```bash
python scripts/kc_phu_department_students_begin.py
python scripts/kc_phu_department_students_begin.py --drill-agent mirror_warden
```

MCP: `tsap_blackmask_drill`  
MAO: `mao_blackmask_drill`

## Departments

| Department | Parent | Lane | Students (sub-brains) |
|------------|--------|------|------------------------|
| `kopano_labs_experimentation` | Kopano Labs | experimentation | All Kopano Labs sub-brains |
| `ama_phu_creativity` | Ama-Phu Entertainment | creativity | AMA-PHU Entertainment (+ mirror warden focus) |

## Begin operation

```bash
# Begin all department students + BlackMask gate
python scripts/kc_phu_department_students_begin.py

# API (public status)
GET /api/kc/phu/apprenticeship/status
POST /api/kc/phu/apprenticeship/begin-students
```

## MCP config

Add `tsap` server — see `.cursor/mcp.json` and `CLI/tsap_mcp_config.json`.

## MAO tools

- `mao_tsap_student_turn`
- `mao_tsap_teacher_turn`
- `mao_blackmask_drill`
- `mao_department_status`
