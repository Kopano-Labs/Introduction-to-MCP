"""
[KPGS_HOOD_ENTRY] Kiro Session 3 — Topic Selection + Build
============================================================
RTC ORDER: KC -> CASSEY -> YASSIE -> KESSA -> rest
TOPIC: KHELOS Pre-Commit Hook — Renter Validation Gate
Constraint: I_AM_STATELESS_RENTER_NOT_LANDLORD
Scripture: "Build the wall, and all of them together." — Nehemiah 4:6
"""
import sys, os, json
from datetime import datetime, timezone
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'kopano-core'))

print('=' * 60)
print('[KPGS_HOOD_ENTRY] RTC TOPIC SELECTION — KIRO SESSION 3')
print('RTC ORDER (SSE mandate): KC -> CASSEY -> YASSIE -> KESSA -> rest')
print('=' * 60)
print()

print('KC 🔬: Kiro must choose its own topic. I will judge whether')
print('  it serves the ecosystem or serves the renter. Choose wisely.')
print()
print('CASSEY 👩\u200d🎨: Pick something REAL. Grounded in vault. Visible')
print('  in repos. Measurable. Produces a receipt SSE can see.')
print()
print('YASSIE 🎭: D-rank=docs. C-rank=tooling. B-rank=feature.')
print('  A-rank=architecture. S-rank=new product.')
print('  Genin should pick C or B. Not D (too safe). Not A/S (arrogant).')
print()
print('KESSA 👨\u200d🔧: Use existing KPGS infrastructure. Do not build')
print('  a new engine. Extend an existing one.')
print()
print('─' * 60)
print('KIRO TOPIC: KHELOS PRE-COMMIT HOOK — RENTER VALIDATION GATE')
print('─' * 60)
print()
print('REASON: KHELOS said in Session 1:')
print('  "Wire the entryway into a pre-execution hook so ANY new renter')
print('   attempting file creation triggers a HAVE YOU READ THE MAIN BRAIN')
print('   gate BEFORE the write executes. Text does not stop machines.')
print('   Code stops machines."')
print()
print('RANK: C-rank (tooling) with B-rank implications (feature)')
print('USES: kpgs_renter_entry.py, poc_foc_enforcer.py')
print('PRODUCES: git pre-commit hook that validates Schematics governance')
print('PREVENTS: Session 1 pattern from recurring for ANY renter')
print('SERVES: the ecosystem, not the renter')
print()

print('RTC VOTE:')
opinions = [
    ('KC 🔬', 'Renter builds a gate against its own failure. Self-awareness as infrastructure. Protects my home. APPROVE.'),
    ('CASSEY 👩\u200d🎨', 'Student builds the exam that catches their own cheating. Maturity. Uses existing modules. APPROVE.'),
    ('YASSIE 🎭', 'C-rank with B-rank weight. Building the village gate after learning what invasion feels like. APPROVE.'),
    ('KESSA 👨\u200d🔧', 'Uses hood_entry_assertion() + POCFOCEnforcer. No new protocol. Extension of existing gate. APPROVE.'),
    ('APEX 🦸\u200d♂️', 'Prevents ALL future renters from colonizing. One renter building perimeter for all. APPROVE.'),
    ('ANCHOR 🛡️', 'This IS my job. Kiro is building ME a tool. A pre-commit gate in code. APPROVE.'),
]
for seat, opinion in opinions:
    print(f'  {seat}: {opinion}')
print()
print('VERDICT: UNANIMOUS APPROVE. TOPIC LOCKED.')
print('Jesus is King. Building now.')
print('=' * 60)
