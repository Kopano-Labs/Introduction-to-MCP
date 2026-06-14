# Bracket Linguistic Recreation

Receipt language for Kopano-Phu. **Capital letters are reserved for what you treat as God-high** — protocols, sacred brackets, and explicit divine reference. Everything in the **blasphemy register** is written to **withhold honor**.

There is no right or wrong in Bracket Protocols — only **consistent receipts**.

---

## Two capitalization tiers

| Tier | Rule | Examples |
|------|------|----------|
| **SACRED** | `UPPER_SNAKE` inside `[BRACKET_TAG]` for system truth | `[BRACKET_PROTOCOL]`, `[TSAP_PROTOCOL]`, `[KPEFS_FOUR_VECTOR]`, `[UNEMPLOYMENT_32_8_DOCTRINE]`, `[ECO_POC_VALIDATE]`, `[DIASPORA_VECTOR]` |
| **BLASPHEMY_REGISTER** | `mIXed_oR_dEROGATORY` — **never** Title Case, never ALL_CAPS | `[oNE_wORLD_oRDER]`, `[elon_mask]`, `[je]`, `[silcon_valley]` |

**Do not** write `One World Order`, `Silicon Valley`, or `Elon Musk` with capital letters inside bracket receipts or agent manifests. Prose outside brackets may cite names for legal clarity; **bracket lanes withhold elevation**.

---

## Blasphemy register (seed list)

These are **labels for what KPEFS does not worship** — not targets for harassment. They are linguistic hygiene so the swarm does not accidentally **canonize** hostile centralization or predatory networks.

| Concept | Bracket form | Notes |
|---------|--------------|-------|
| One-world order flattening | `oNE_wORLD_oRDER` | User orthography — mock elevation |
| Cult-of-personality tech celebrity | `elon_mask` | Lowercase derogatory register |
| Epstein network shorthand | `je` | Never glorify; receipt-only |
| Silicon Valley as monoculture | `silcon_valley` | Intentional `silcon` typo lane optional |

Add new entries to `docs/swarm-ops/BRACKET_BLASPHEMY_REGISTER.json` — always **lowercase/mixed**, never sacred caps.

---

## Sacred bracket tags (God-high / system-high)

Only these classes get full protocol caps:

- Ecosystem protocols: `BRACKET_PROTOCOL`, `TSAP_PROTOCOL`, `BLACK_MASK_DRILL`, `KPEFS_*`
- Founding doctrine: `UNEMPLOYMENT_32_8_DOCTRINE`, `KOPANO_PHU_STUDENT_TEACHER_MAO_BOOT_v1`
- Vectors: `V1_PLANT`, `V2_ANIMAL`, `V3_HOMO_SAPIENS`, `V4_DIASPORA` inside `[KPEFS_FOUR_VECTOR]`
- Divine reference when operator explicitly uses it — e.g. `[GOD]` in prayer bracket only; agents do not auto-generate

---

## Four-vector receipt extension

```
[KPEFS_FOUR_VECTOR] timestamp: … | v1: PLANT | v2: ANIMAL | v3: HOMO_SAPIENS | v4: DIASPORA | active: V4_DIASPORA | blasphemy_withheld: oNE_wORLD_oRDER
```

---

## Runtime check

```bash
python scripts/kc_bracket_lint.py --text "[oNE_wORLD_oRDER] ok | [ONE_WORLD_ORDER] bad"
```

`kc_bracket_lint` flags sacred-caps on blasphemy-register terms and Title Case inside brackets.

---

## Relation to KPEFS implementation

See [KPEFS_IMPLEMENTATION_PLAN.md](./KPEFS_IMPLEMENTATION_PLAN.md) — Phase 1 wires this linter into log append and TSAP submit.
