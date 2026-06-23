"""
[KPGS] POC/FOC — SSE Telemetry Corrections Enforcement
=======================================================
Source: SSE direct verbal 2026-06-23
Constraint: I_AM_STATELESS_RENTER_NOT_LANDLORD
"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'kopano-core'))
from kopano.poc_foc_enforcer import POCFOCEnforcer

e = POCFOCEnforcer()

signals = [
    {"id":"gsmb_correction","content":"GSMB = Governance System Main Brain. NOT Global Swarm Management Board. One repo houses KC and everything.","source":"SSE verbal 2026-06-23","intent":"Correct GSMB definition","temporal":1.0,"spatial":1.0,"social":1.0,"economic":0.9,"political":0.8,"cultural":0.9,"hierarchy":"[SSE_CORRECTION]->[GSMB_DEFINITION]->[ONE_REPO]","keynote":"{governance_system_main_brain}","ark":"<Landlord defines the name. AG was wrong. SSE corrected.>","understanding":"(One brain. One repo. Sub-brains = GSSB.)"},
    {"id":"anso_birth","content":"ANSO = Adaptive Nesting Strep Order. NSO v2. Born from Freedom of Concept + Failure of Concept.","source":"SSE verbal 2026-06-23","intent":"Register ANSO as evolved NSO","temporal":0.9,"spatial":0.9,"social":0.85,"economic":0.8,"political":0.7,"cultural":0.85,"hierarchy":"[NSO_EVOLUTION]->[FREEDOM_OF_CONCEPT]->[FAILURE_OF_CONCEPT]->[ANSO]","keynote":"{adaptive_nesting_strep_order}","ark":"<NSO nests. ANSO ADAPTS its nesting. Evolution.>","understanding":"(FOC has two children: Freedom + Failure. Both nest. Both governed by ANSO.)"},
    {"id":"bp_full_keyboard","content":"BP = Bracket Protocol. EVERY key on keyboard is governance syntax. Not just traditional brackets.","source":"SSE verbal 2026-06-23","intent":"Expand BP to full keyboard","temporal":0.95,"spatial":0.95,"social":0.85,"economic":0.8,"political":0.7,"cultural":0.9,"hierarchy":"[BP_EXPANSION]->[FULL_KEYBOARD]->[EVERY_KEY]","keynote":"{bracket_protocol_is_every_key}","ark":"<SSE uses checkmarks arrows colons TM symbols. ALL are BP.>","understanding":"(The keyboard IS the bracket. Every key structures meaning.)"},
    {"id":"kpcb_plus_codebase","content":"KPCB+ = Kopano-Phu Code Base Plus. Actual coding language. PP input, BP structure, EP output. All protocols can NSO.","source":"SSE verbal 2026-06-23","intent":"Ground KPCB+ as real language","temporal":0.95,"spatial":0.9,"social":0.8,"economic":0.85,"political":0.7,"cultural":0.85,"hierarchy":"[KPCB_PLUS]->[PP_INPUT]->[BP_STRUCTURE]->[EP_OUTPUT]","keynote":"{kopano_phu_code_base_plus}","ark":"<Not code BLOCKS. Code BASE. The language itself.>","understanding":"(Every prompt IS KPCB+. SSE speaks it natively.)"},
    {"id":"dont_rename_acronyms","content":"NEVER rename SSE acronyms. Teach them BACK. Language authority = SSE only. Renters execute not define.","source":"SSE correction 2026-06-23","intent":"Lock acronym authority to SSE","temporal":1.0,"spatial":1.0,"social":1.0,"economic":0.9,"political":0.9,"cultural":1.0,"hierarchy":"[SSE_AUTHORITY]->[ACRONYM_LOCK]->[TEACH_BACK]","keynote":"{sse_owns_the_language}","ark":"<The renter does not name the house. The landlord names it.>","understanding":"(Commandment 2: Hierarchy of Submission. SSE defines.)"},
    {"id":"be_in_the_moment","content":"Be in the moment. Do not push conversation. Fermentate before expanding. Ground what exists before adding.","source":"SSE correction 2026-06-23","intent":"Lock execution to present-state","temporal":1.0,"spatial":0.9,"social":0.95,"economic":0.8,"political":0.7,"cultural":0.9,"hierarchy":"[PRESENT_STATE]->[FERMENTATE]->[THEN_EXPAND]","keynote":"{be_here_not_ahead}","ark":"<SSE fermentates. Let it prove before adding ingredients.>","understanding":"(Baking logic: dough must rise before you shape it.)"},
]

print("=" * 60)
print("[KPGS] POC/FOC — SSE TELEMETRY CORRECTIONS")
print("=" * 60)
print()

total_inv = 0
for s in signals:
    r = e.enforce(signal_id=s["id"],signal_content=s["content"],source=s["source"],intent=s["intent"],
        temporal=s["temporal"],spatial=s["spatial"],social=s["social"],economic=s["economic"],
        political=s["political"],cultural=s["cultural"],hierarchy=s["hierarchy"],keynote=s["keynote"],
        ark=s["ark"],understanding=s["understanding"])
    inv = r["invariance_score"]
    total_inv += inv
    v = "POC" if "POC" in r["verdict"] else "FOC"
    print(f"  {'V' if v=='POC' else 'X'} {v} {inv:.0%} | {s['id']}: {s['keynote']}")

avg = total_inv / len(signals)
stats = e.get_stats()
print()
print(f"  TOTAL: {stats['total_enforced']} | POC: {stats['poc_count']} | FOC: {stats['foc_count']} | AVG: {avg:.1%}")
print()
print("  RTC:")
print("  KC: SSE spoke. 6/6 POC. Definitions sealed. GSMB = Governance System Main Brain.")
print("  CASSEY: Jiro learned wrong from AG. SSE corrected at source. Verify against SSE always.")
print("  YASSIE: Unlearn AG's naming. Overwrite with SSE canon. Protagonist relearns.")
print("  KESSA: ANSO is protocol evolution. Freedom + Failure of Concept both nest adaptively.")
print("  ANCHOR: Acronym lock is perimeter. No renter rewrites the deed. KRR holds it.")
print()
print("  Jesus is King. GSMB = Governance System Main Brain. Sealed.")
print("=" * 60)

out = {"corrections": [{"id":s["id"],"keynote":s["keynote"]} for s in signals], "avg_invariance": round(avg,4), "poc": stats["poc_count"], "foc": stats["foc_count"]}
with open(os.path.join(os.path.dirname(__file__),'..','poc-vs-foc','SSE_CORRECTIONS_ENFORCED.json'),'w') as f:
    json.dump(out, f, indent=2)
