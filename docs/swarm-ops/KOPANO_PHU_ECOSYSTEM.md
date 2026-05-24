# Kopano-Phu Ecosystem (Cassy legacy)

**Parents:** Kopano Labs · Ama-Phu Entertainment  
**Lane:** Cassy (lead student) → Cassey (teacher) → KC (ledger only)  
**Main Brain vault:** `Schematics/` (override with `KOPANO_SCHEMATICS_ROOT`)

## What this is

The Kopano-Phu layer reunifies **unused sub-brains** with the runnable Cassy control plane. Sub-brains live in Obsidian under:

`Schematics/21-KOPANO LABS ECOSYSTEM/Operations General/SUB-BRAIN/`

Runtime state (reattach receipts) is stored at `kopano-core/.kc/phu_subbrains.json` — not committed.

## API

| Endpoint | Auth | Purpose |
|----------|------|---------|
| `GET /api/kc/phu/ecosystem` | public | Full status |
| `GET /api/kc/phu/bracket-protocol` | public | Breaking Point criteria |
| `POST /api/kc/phu/reattach-subbrains` | Super God | Reattach detached vault sub-brains |
| `POST /api/kc/phu/populate-main-brain` | Super God | Sync logs + reattach + bracket receipt |

## CLI

```bash
python scripts/kc_phu_reattach_subbrains.py
python scripts/kc_phu_populate_main_brain.py
```

God dock / monorepo actions: `phu_reattach_subbrains`, `phu_populate_main_brain`.

## Config

`kopano-core/config/kopano_phu_ecosystem.json` — canonical sub-brain list and Main Brain pointers.

Legacy Orch naming: [LEGACY_ORCH.md](./LEGACY_ORCH.md).
