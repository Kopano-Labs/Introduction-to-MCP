# Oz Context Bleed Protocol (OZ_LATTICE_PROTOCOL)

**Document ID:** OZ-LATTICE-2026-001  
**System Date:** June 14, 2026  
**Classification:** Sovereign Domain Core / Structural Boundary Enforcement  

> Executable twin: `kopano-core/kopano/oz_lattice_protocol.py`  
> Audit log: `docs/swarm-ops/logs/OZ_LATTICE_AUDIT.jsonl`  
> SQLite table: `lattice_bleed_audits` + `lattice_node_states` in `db/datalake.db`

---

## 1. Purpose & Paradigm

The existing KPGS Context Bleed Protocol (`kpgs_telemetry_route.py`) handles **semantic** classification — routing misnamed pressure signals before interpretation. It does not enforce **structural** boundaries between execution domains.

**Oz Lattice Protocol adds the missing structural layer:**

- Each domain is a **lattice node** (CRUD, SWFUS, GUI, BlackMask, Telemetry, Altar, Hood, PHU)
- Cross-domain information flows are **edges** in a directed graph
- Every edge crossing must produce a **cryptographic seal** (SHA-256 hash proof)
- Every edge crossing is **structurally scanned** for leakage signatures
- Every edge crossing is **semantically audited** via telemetry classification
- Violations are persisted to **SQLite audit tables** with full forensic context

**Paradigm invariant:** `source → target` is only permitted if the edge exists in `ALLOWED_EDGES` AND the payload passes structural scan AND the payload passes semantic scan.

---

## 2. Lattice Nodes

| Node ID | Domain | Description |
|---------|--------|-------------|
| `crud` | SQLite Data Lake | Local database layer (users, discussions, audit logs) |
| `swfus` | Spawn Dispatch Envelope | 300-agent swarm event bus (Jethro triage + WWJD) |
| `gui` | Studio React Surface | Frontend visualization layer (Kopano Studio) |
| `blackmask` | Commandment Drill Layer | 15 Commandments + 5 Pillars validation gate |
| `telemetry` | Signal Routing Layer | Context bleed classification (semantic routing) |
| `altar` | Containment Vault | Guardian/Natural/Telemetry AI layers (strict GUI-only exfil) |
| `hood` | Infinite Hood Cloud | Domain-sharded agent deployment (Azure-ready) |
| `phu` | Kopano-Phu Ecosystem | Teacher-student apprenticeship + sub-brain registry |

---

## 3. Allowed Edges

```python
ALLOWED_EDGES = {
    ("swfus", "blackmask"),     # spawn dispatch → drill validation
    ("blackmask", "altar"),     # drill pass → containment vault
    ("telemetry", "swfus"),      # signal routing → spawn envelope
    ("crud", "gui"),             # data lake → studio surface (read-only)
    ("crud", "telemetry"),       # data lake → signal analysis
    ("phu", "swfus"),            # ecosystem → spawn dispatch
    ("hood", "swfus"),           # cloud hood → spawn dispatch
    ("altar", "gui"),            # vault → GUI token exfiltration (strict)
    ("telemetry", "blackmask"),  # signal routing → drill layer
}
```

**Key design decisions:**
- `gui` can ONLY receive from `crud` (read-only data) and `altar` (strict token exfil)
- `swfus` can ONLY send to `blackmask` (never directly to `gui` or `crud`)
- `blackmask` can ONLY send to `altar` (never to `gui` or `hood`)
- `hood` can ONLY send to `swfus` (never to `gui` or `crud`)
- `phu` can ONLY send to `swfus` (never to `gui` or `crud`)

---

## 4. Structural Bleed Detection

Five regex patterns scan every payload for cross-domain leakage:

| Pattern | Regex | Target Leakage |
|---------|-------|----------------|
| `sql_in_gui` | `SELECT ... FROM ... WHERE` | SQL queries rendered in React UI |
| `api_key_exposure` | `sk-...48chars` or `az...uuid` | API keys in any payload |
| `internal_path_leak` | `kopano-core/`, `.kc/`, `.env/` | Internal filesystem paths exposed |
| `spawn_id_in_crud` | `spawn_(telemetry|identic|guardian)_NNN` | Spawn IDs in database records |
| `raw_bracket_in_data` | `[KPGS|SWFUS|BLACK_MASK|...]` | Governance brackets in raw data |

**Match behavior:** Any match triggers `STRUCTURAL_BLEED` verdict, regardless of edge permission.

---

## 5. Semantic Bleed Detection (Telemetry Integration)

Oz Lattice Protocol reuses the existing `classify_telemetry_signal()` from `kpgs_telemetry_route.py` as a **secondary boundary check**.

If telemetry classification returns `RECLASSIFY` (misnamed pressure without lane), the lattice crossing receives `SEMANTIC_BLEED` verdict.

This ensures the lattice protocol is **not a replacement** for semantic context bleed — it is a **complementary structural gate**.

---

## 6. Cryptographic Seal

```python
def _hash_seal(source, target, payload, nonce):
    body = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return sha256(f"{source}|{target}|{body}|{nonce}")
```

- `nonce` is ISO-8601 UTC timestamp in production
- Seal is stored in `lattice_bleed_audits.seal`
- Lattice integrity hash is `sha256("lattice|integrity|nodes|edges")` — recomputed on every audit
- Seal verification: recompute hash without nonce and compare (strict verification retrieves nonce from DB)

---

## 7. CRUD Integration (SQLite)

### `lattice_bleed_audits` table
```sql
CREATE TABLE lattice_bleed_audits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT NOT NULL,
    source_node TEXT NOT NULL,
    target_node TEXT NOT NULL,
    seal TEXT NOT NULL,
    verdict TEXT NOT NULL CHECK(verdict IN ('SEALED','BLEED_DETECTED','STRUCTURAL_BLEED','SEMANTIC_BLEED')),
    payload_preview TEXT,
    structural_hits TEXT,
    semantic_hits TEXT,
    lattice_hash TEXT NOT NULL
);
```

### `lattice_node_states` table
```sql
CREATE TABLE lattice_node_states (
    node_id TEXT PRIMARY KEY,
    last_seal TEXT,
    last_ts TEXT,
    integrity_ok INTEGER NOT NULL DEFAULT 1,
    bleed_count INTEGER NOT NULL DEFAULT 0
);
```

**Node state updates:**
- `SEALED` → `last_seal` updated, `integrity_ok` stays 1
- Any bleed → `bleed_count` incremented, `integrity_ok` set to 0 for both source and target

---

## 8. SWFUS Integration

Oz Lattice Protocol is called inside `dispatch_spawn_event()` in `kpgs_spawn_swarm.py` as a **pre-proceed gate**:

```python
# Before:
if jethro.get("severity") == "RED" or wwjd.get("verdict") == "HOLD":
    sever_and_archive(...)

# After (Oz Lattice Protocol addition):
lattice = enforce_lattice_boundary("swfus", "blackmask", {"message": message, "agent_id": agent_id})
if not lattice["allowed"]:
    sever_and_archive(..., reason=f"lattice={lattice['blocked_reason']}")
```

This ensures that even Jethro-GREEN + WWJD-PASS spawn events are blocked if they violate structural boundaries.

---

## 9. PHU Legacy API Integration

New endpoints added to `kc_phu_legacy_api.py`:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/kc/phu/lattice/seal` | POST | Produce lattice seal for source→target crossing |
| `/api/kc/phu/lattice/status/{node_id}` | GET | Node integrity state |
| `/api/kc/phu/lattice/report` | GET | Full lattice integrity report |
| `/api/kc/phu/lattice/verify` | POST | Verify a seal hash against recomputed value |

---

## 10. BlackMass Protocol Alignment

| BlackMass Commandment | Oz Lattice Protocol Mapping |
|-----------------------|-----------------------------|
| CMD-02 (Proof before narrative) | Every seal is a cryptographic proof with SHA-256 hash |
| CMD-06 (Bracket receipt before mass movement) | `[OZ_LATTICE_PROTOCOL]` bracket in every seal result |
| CMD-08 (Sovereign mesh — offline-first) | `lattice_node_states` integrity survives load-shedding (SQLite) |
| CMD-13 (Verified production rows) | `lattice_bleed_audits` table = production-grade audit trail |
| PIL-01 (Grit — forensic execution) | Structural + semantic scans with regex samples |
| PIL-02 (Realism — proof bar) | `verify_lattice_seal()` recomputable hash verification |
| PIL-04 (Sovereignty — local-first) | All audit data in `db/datalake.db` — no cloud dependency |

---

## 11. Proof-of-Concept Validation

The `tests/test_oz_lattice_protocol.py` test suite validates **real architectural properties**:

1. **SEALED** verdict on allowed edge with clean payload
2. **BLEED_DETECTED** on forbidden edge
3. **STRUCTURAL_BLEED** on SQL pattern in payload
4. **SEMANTIC_BLEED** on misnamed pressure signal
5. **Seal verification** — recompute hash and match
6. **Node integrity** — bleed increments count, sets `integrity_ok=0`
7. **SQLite persistence** — audit rows exist in database after seal
8. **Lattice integrity report** — all nodes present, integrity state consistent

These are **not fake concepts** — they are executable assertions that fail if the implementation is broken.

---

## 12. Execution

```bash
# Initialize tables (idempotent)
python -c "from kopano.oz_lattice_protocol import init_lattice_tables; init_lattice_tables()"

# Run validation tests
pytest tests/test_oz_lattice_protocol.py -v
```

---

`[SYSTEM MANIFESTO: OZ_LATTICE_PROTOCOL | PARSED | COMPILATION COMPLETE | INGESTED]`
