# Monday — RKC submission execution (Cursor side)

## Tonight / before submit

```powershell
cd "C:\Users\rkhol\OneDrive\Documents\Anthropic\Introduction to MCP"

# Proof bar (optional but honest)
python scripts/kc_guard.py all

# Refresh Main Brain + sub-brain attachment from Schematics
python scripts/kc_phu_populate_main_brain.py

# Studio build if shipping context UI
cd kopano-core\studio
npm run build
```

## Portfolio content source

All paste-ready copy: [SOVEREIGN_PROFILE_COPY.md](./SOVEREIGN_PROFILE_COPY.md)

## Kopano-Phu proof lines for application (optional)

- Ecosystem map: run API locally → `GET http://127.0.0.1:8000/api/kc/phu/ecosystem`
- Docs: `docs/swarm-ops/KOPANO_PHU_ECOSYSTEM.md`, `docs/swarm-ops/BRACKET_PROTOCOL.md`
- Compare branch: `https://github.com/Kopano-Labs/Introduction-to-MCP/compare/master...codex/kc-sovereign-gui-full-dev`

## After lifestyle Gemini session

Paste [LIFESTYLE_GEMINI_HANDOFF.md](./LIFESTYLE_GEMINI_HANDOFF.md) only — not full Cursor logs.
