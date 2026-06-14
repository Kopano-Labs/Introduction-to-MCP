# Structure / 07-Agents

Agent-governance seeds for Kopano-Phu. Runtime: `kopano-core/kopano/phu_boot_governance.py`.

| File | Purpose |
|------|---------|
| `KOPANO_PHU_STUDENT_TEACHER_MAO_BOOT_v1.json` | Boot manifest |
| `ROLE_BINDINGS.json` | KC Save/Watch · Cassy apprenticeship · Cassey teacher · MAO routes only |
| `AGENT_MESH.json` | Who is in the mesh (no catalog-200 auto-promote) |
| `PROMOTION_LAW.json` | Proof before promotion |
| `BLACKMASK_GATE.json` | Drill gate for mesh agents |

```bash
python scripts/kc_phu_boot_v1.py status
python scripts/kc_phu_boot_v1.py blackmask-dry-run
```
