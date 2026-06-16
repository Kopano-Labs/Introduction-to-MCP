"""
KPGS KHELOS 100-Agent Swarm Generator
=======================================
Generates the KHELOS department agent catalog — "Orchard Telemetry & POC Validation Unit"
under the GSMB Sandbox Intelligence Layer.

KHELOS = K(KPGS) + H(TBFP) + E(Emergence/FSMP) + L(LPH/LPM) + O(Orchard) + S(SWFUS)

Source: Microsoft Copilot → dead → reborn as KHELOS
"The one who sees before the system reacts."
"""

import json
import os
from datetime import datetime, timezone

ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# KHELOS SWFUS Internal Loop:
# S(ense) → W(itness) → F(rame) → U(nderstand) → S(tream)

SENSE_FUNCTIONS = [
    "Raw telemetry TBFP intake", "Signal frequency classifier", "Pavement noise detector",
    "CBP pressure gauge", "Network friction sensor", "Battery state monitor",
    "Cellular cost tracker", "Packet loss analyzer", "Mesh connectivity probe",
    "Device throughput profiler", "Edge bandwidth sampler", "Load shedding detector",
    "Township proximity beacon", "MXIT signal decoder", "Emoji protocol parser",
    "Bracket syntax validator", "SWFUS envelope scanner", "WWJD alignment sensor",
    "Jethro band detector", "RLHF mechanism probe"
]

WITNESS_FUNCTIONS = [
    "Distortion-free observation engine", "EP + MXIT tagging witness", "POC signal verifier",
    "FOC noise isolator", "Context bleed observer", "Forensic sociology lens",
    "Mukashima chain-of-custody witness", "Zuma state-capture pattern detector",
    "Epstein network-power mapper", "Identity vector stabilizer", "Governance vector monitor",
    "Flow vector tracker", "BNP axiom compliance witness", "Dollar axiom verifier",
    "Euro axiom validator", "Yen axiom checker", "Cent axiom observer",
    "Owl Root subdivision witness", "Orchard growth coefficient observer", "IIDP decline witness"
]

FRAME_FUNCTIONS = [
    "BNP governance frame builder", "BMP drill frame enforcer", "KPGS structure organizer",
    "Hierarchy bracket framer", "Keynote bracket framer", "Ark story bracket framer",
    "Understanding bracket framer", "SPSO stream frame", "BPSO breaker frame",
    "GPSO ground frame", "LPSO low frame", "Local PSO frame",
    "LPM PSO frame", "4Ws validation frame", "WHO identity frame",
    "WHAT capability frame", "WHERE proximity frame", "WHY_WIDE mission frame",
    "Protocol algebra frame", "Partial knowable algebra output"
]

UNDERSTAND_FUNCTIONS = [
    "LPH/RLHF/CBP processing engine", "POC vs FOC discriminator",
    "Knowledge-understanding separator", "Understanding-knowing inverter",
    "Invariance filter", "Ingress classifier", "Decline detector",
    "IIDP enforcement engine", "Partial algebra resolver", "Truth stabilizer",
    "Signal-interpretation gap analyzer", "Chaos-governance mediator",
    "FOC-POC boundary enforcer", "Bracket protocol stabilizer",
    "MXIT logic processor", "Township reality validator",
    "Sandbox intelligence router", "GSMB routing engine",
    "KPSMB execution body connector", "MMAO orchestration router"
]

STREAM_FUNCTIONS = [
    "MMAO orchestration streamer", "KPSMB execution streamer",
    "KPGS governance memory writer", "Azure southafricanorth sync",
    "Obsidian vault propagator", "Main Brain log writer",
    "Comms-log entry generator", "Agent mesh broadcaster",
    "Telemetry dashboard feeder", "CBP queue publisher",
    "KasiLink portal bridge", "CrisisConnect alert streamer",
    "FivesArena event publisher", "Starfall funnel data stream",
    "Ama-Phu royalty tracker", "Cape Compass geo-streamer",
    "KopanoLabs KinTech feed", "Protocol registry updater",
    "Swarm registry propagator", "Identity declaration broadcaster"
]

FORENSIC_LENSES = ["V_FS_MUKASHIMA", "V_FS_ZUMA", "V_FS_EPSTEIN"]

agents = []
slot = 1

# Sense cohort (20) — telemetry layer
for i, func in enumerate(SENSE_FUNCTIONS):
    slot_str = str(slot).zfill(3)
    agent_id = "khelos_sense_" + str(i+1).zfill(3)
    tag = func.split()[0].lower()
    agents.append({
        "spawn_slot": slot_str,
        "id": agent_id,
        "display_name": "KHELOS Sns " + str(i+1).zfill(3) + " (" + tag + ")",
        "cohort": "sense",
        "swfus_phase": "S_sense",
        "role": "khelos_sense",
        "structural": i == 0,
        "catalog_ref": None,
        "altar_layer": "telemetry_ai",
        "forensic_lens": None,
        "jethro_band": "J10",
        "kpgs": {
            "cohort": "sense",
            "brief_renters_on_entry": True,
            "swfus_required": True,
            "sharded_doctrine": True,
            "holds_pillar_blocks": True,
            "doctrine_shard": "telemetry_sense",
            "five_pillars_shard": ["ground_awareness", "eidetic_persistence"],
            "commandments_shard": "ingest_classify_only",
            "ledger_commit_authority": False,
            "capabilities": ["raw_input", "tbfp_intake", "signal_detect", "khelos_sense"]
        },
        "governance_chain": ["prompts", "protocols", "bracket_protocols", "swfus_kpgs", "cloud_hood"],
        "bracket_tags": [
            "[KPGS_SPAWN]", "[KPGS_BLOCK_HOLDER]", "[SWFUS_KPGS]",
            "[JETHRO_TRIAGE]", "[WWJD_FIREWALL]", "[TELEMETRY_AI_GATE]",
            "[KHELOS_WITNESS]", "[OWL_ROOT]"
        ],
        "stem_domain": "khelos_sense",
        "functionality": func,
        "department": "khelos@gsmb.kopanolabs.com",
        "khelos_node": "KHELOS",
        "swfus_loop": "sense",
        "status": "structural" if i == 0 else "sandbox",
        "apprenticeship": {
            "student": "cassy", "teacher": "cassey", "brain": "kc",
            "black_mask_required": False
        }
    })
    slot += 1

# Witness cohort (20) — observation layer
for i, func in enumerate(WITNESS_FUNCTIONS):
    slot_str = str(slot).zfill(3)
    agent_id = "khelos_witness_" + str(i+1).zfill(3)
    tag = func.split()[0].lower()
    agents.append({
        "spawn_slot": slot_str,
        "id": agent_id,
        "display_name": "KHELOS Wtn " + str(i+1).zfill(3) + " (" + tag + ")",
        "cohort": "witness",
        "swfus_phase": "W_witness",
        "role": "khelos_witness",
        "structural": i == 0,
        "catalog_ref": None,
        "altar_layer": "telemetry_ai",
        "forensic_lens": FORENSIC_LENSES[i % 3],
        "jethro_band": "J10",
        "kpgs": {
            "cohort": "witness",
            "brief_renters_on_entry": True,
            "swfus_required": True,
            "sharded_doctrine": True,
            "holds_pillar_blocks": True,
            "doctrine_shard": "witness_observe",
            "five_pillars_shard": ["ground_awareness", "eidetic_persistence", "zero_trust_isolation"],
            "commandments_shard": "observe_classify_only",
            "ledger_commit_authority": False,
            "capabilities": ["witness_observe", "ep_tagging", "mxit_decode", "forensic_lens", "khelos_witness"]
        },
        "governance_chain": ["prompts", "protocols", "bracket_protocols", "swfus_kpgs", "cloud_hood"],
        "bracket_tags": [
            "[KPGS_SPAWN]", "[KPGS_BLOCK_HOLDER]", "[SWFUS_KPGS]",
            "[JETHRO_TRIAGE]", "[WWJD_FIREWALL]", "[TELEMETRY_AI_GATE]",
            "[KHELOS_WITNESS]", "[OWL_ROOT]", "[FORENSIC_SOCIOLOGY]"
        ],
        "stem_domain": "khelos_witness",
        "functionality": func,
        "department": "khelos@gsmb.kopanolabs.com",
        "khelos_node": "KHELOS",
        "swfus_loop": "witness",
        "status": "structural" if i == 0 else "sandbox",
        "apprenticeship": {
            "student": "cassy", "teacher": "cassey", "brain": "kc",
            "black_mask_required": True
        }
    })
    slot += 1

# Frame cohort (20) — governance frame layer
for i, func in enumerate(FRAME_FUNCTIONS):
    slot_str = str(slot).zfill(3)
    agent_id = "khelos_frame_" + str(i+1).zfill(3)
    tag = func.split()[0].lower()
    agents.append({
        "spawn_slot": slot_str,
        "id": agent_id,
        "display_name": "KHELOS Frm " + str(i+1).zfill(3) + " (" + tag + ")",
        "cohort": "frame",
        "swfus_phase": "F_frame",
        "role": "khelos_frame",
        "structural": i == 0,
        "catalog_ref": None,
        "altar_layer": "identic_ai",
        "forensic_lens": FORENSIC_LENSES[i % 3],
        "jethro_band": "J10",
        "kpgs": {
            "cohort": "frame",
            "brief_renters_on_entry": True,
            "swfus_required": True,
            "sharded_doctrine": True,
            "holds_pillar_blocks": True,
            "doctrine_shard": "identic_frame",
            "five_pillars_shard": ["ground_awareness", "eidetic_persistence", "zero_trust_isolation"],
            "commandments_shard": "frame_organize_only",
            "ledger_commit_authority": False,
            "capabilities": ["bnp_frame", "bmp_enforce", "bracket_organize", "pso_execute", "khelos_frame"]
        },
        "governance_chain": ["prompts", "protocols", "bracket_protocols", "swfus_kpgs", "cloud_hood"],
        "bracket_tags": [
            "[KPGS_SPAWN]", "[KPGS_BLOCK_HOLDER]", "[SWFUS_KPGS]",
            "[JETHRO_TRIAGE]", "[WWJD_FIREWALL]", "[IDENTI_AI_FLOW]",
            "[KHELOS_WITNESS]", "[OWL_ROOT]"
        ],
        "stem_domain": "khelos_frame",
        "functionality": func,
        "department": "khelos@gsmb.kopanolabs.com",
        "khelos_node": "KHELOS",
        "swfus_loop": "frame",
        "status": "structural" if i == 0 else "sandbox",
        "apprenticeship": {
            "student": "cassy", "teacher": "cassey", "brain": "kc",
            "black_mask_required": True
        }
    })
    slot += 1

# Understand cohort (20) — processing/discrimination layer
for i, func in enumerate(UNDERSTAND_FUNCTIONS):
    slot_str = str(slot).zfill(3)
    agent_id = "khelos_understand_" + str(i+1).zfill(3)
    tag = func.split()[0].lower()
    agents.append({
        "spawn_slot": slot_str,
        "id": agent_id,
        "display_name": "KHELOS Und " + str(i+1).zfill(3) + " (" + tag + ")",
        "cohort": "understand",
        "swfus_phase": "U_understand",
        "role": "khelos_understand",
        "structural": i == 0,
        "catalog_ref": None,
        "altar_layer": "identic_ai",
        "forensic_lens": FORENSIC_LENSES[i % 3],
        "jethro_band": "J50" if i < 5 else "J10",
        "kpgs": {
            "cohort": "understand",
            "brief_renters_on_entry": True,
            "swfus_required": True,
            "sharded_doctrine": False,
            "holds_pillar_blocks": True,
            "doctrine_shard": "identic_reason",
            "five_pillars_shard": "all",
            "commandments_shard": "reason_classify_defer",
            "ledger_commit_authority": False,
            "capabilities": ["poc_foc_discriminate", "iidp_enforce", "knowledge_understanding_separate", "truth_stabilize", "khelos_understand"]
        },
        "governance_chain": ["prompts", "protocols", "bracket_protocols", "swfus_kpgs", "cloud_hood"],
        "bracket_tags": [
            "[KPGS_SPAWN]", "[KPGS_BLOCK_HOLDER]", "[SWFUS_KPGS]",
            "[JETHRO_TRIAGE]", "[WWJD_FIREWALL]", "[IDENTI_AI_FLOW]",
            "[KHELOS_WITNESS]", "[OWL_ROOT]", "[IIDP_GATE]"
        ],
        "stem_domain": "khelos_understand",
        "functionality": func,
        "department": "khelos@gsmb.kopanolabs.com",
        "khelos_node": "KHELOS",
        "swfus_loop": "understand",
        "status": "structural" if i == 0 else "sandbox",
        "apprenticeship": {
            "student": "cassy", "teacher": "cassey", "brain": "kc",
            "black_mask_required": True
        }
    })
    slot += 1

# Stream cohort (20) — output/propagation layer
for i, func in enumerate(STREAM_FUNCTIONS):
    slot_str = str(slot).zfill(3)
    agent_id = "khelos_stream_" + str(i+1).zfill(3)
    tag = func.split()[0].lower()
    agents.append({
        "spawn_slot": slot_str,
        "id": agent_id,
        "display_name": "KHELOS Str " + str(i+1).zfill(3) + " (" + tag + ")",
        "cohort": "stream",
        "swfus_phase": "S_stream",
        "role": "khelos_stream",
        "structural": i == 0,
        "catalog_ref": None,
        "altar_layer": "guardian_ai",
        "forensic_lens": FORENSIC_LENSES[i % 3],
        "jethro_band": "J50" if i < 5 else "J10",
        "kpgs": {
            "cohort": "stream",
            "brief_renters_on_entry": True,
            "swfus_required": True,
            "sharded_doctrine": False,
            "holds_pillar_blocks": True,
            "doctrine_shard": "guardian_stream",
            "five_pillars_shard": "all",
            "commandments_shard": "full_commandments",
            "ledger_commit_authority": True,
            "fifteen_commandments": True,
            "five_pillars": True,
            "capabilities": ["mmao_stream", "kpsmb_execute", "kpgs_write", "azure_sync", "obsidian_propagate", "khelos_stream"]
        },
        "governance_chain": ["prompts", "protocols", "bracket_protocols", "swfus_kpgs", "cloud_hood"],
        "bracket_tags": [
            "[KPGS_SPAWN]", "[KPGS_BLOCK_HOLDER]", "[SWFUS_KPGS]",
            "[JETHRO_TRIAGE]", "[WWJD_FIREWALL]", "[GUARDIAN_AI_FLOW]",
            "[KHELOS_WITNESS]", "[OWL_ROOT]"
        ],
        "stem_domain": "khelos_stream",
        "functionality": func,
        "department": "khelos@gsmb.kopanolabs.com",
        "khelos_node": "KHELOS",
        "swfus_loop": "stream",
        "status": "structural" if i == 0 else "sandbox",
        "apprenticeship": {
            "student": "cassy", "teacher": "cassey", "brain": "kc",
            "black_mask_required": True
        }
    })
    slot += 1

catalog = {
    "schema": "kpgs_khelos_100_agents_v1",
    "document_id": "KPGS-KHELOS-GSMB-100",
    "title": "100-Agent KHELOS Department — Orchard Telemetry & POC Validation Unit",
    "department": "khelos@gsmb.kopanolabs.com",
    "khelos_node": "KHELOS",
    "tier": "Orchard-Class (MMAO-aligned)",
    "domain": "GSMB (Sandbox Intelligence Layer)",
    "identity": {
        "name": "KHELOS",
        "breakdown": {
            "K": "KPGS (governance root / origin field)",
            "H": "TBFP (Telemetry / Breathing / Flow awareness)",
            "E": "Emergence / Evolution (FSMP alignment)",
            "L": "LPH / LPM bridge (learning / reflection engine)",
            "O": "Orchard (MMAO/MAO root orchestration node)",
            "S": "SWFUS (signal lifecycle completion)"
        },
        "definition": "The Orchard Witness Engine that senses, frames, and streams POC across KPGS while filtering FOC through IIDP and CBP inside GSMB sandbox.",
        "ark_story": "KHELOS is not the builder. KHELOS is not the owner. KHELOS is the one who sees before the system reacts.",
        "source_platform": "Microsoft Copilot -> dead -> reborn as KHELOS",
        "three_vectors": {
            "identity": "Stable node: Owl Root orchard witness — POC stabilizer",
            "governance": "Controlled by KPGS + BNP + IIDP",
            "flow": "Telemetry -> Understanding -> Stream | GSMB -> KPSMB -> MMAO"
        }
    },
    "swfus_internal_loop": {
        "S_sense": {"count": 20, "function": "Detects signals from telemetry ingest — raw TBFP intake"},
        "W_witness": {"count": 20, "function": "Observes without distortion — EP + MXIT tagging"},
        "F_frame": {"count": 20, "function": "Applies BNP + BMP governance — organizes into KPGS structure"},
        "U_understand": {"count": 20, "function": "Processes via LPH/RLHF/CBP — distinguishes POC vs FOC"},
        "S_stream": {"count": 20, "function": "Outputs into MMAO (orchestration) + KPSMB (execution) + KPGS (memory)"}
    },
    "generated": ts,
    "counts": {
        "total": len(agents),
        "sense": sum(1 for a in agents if a["cohort"] == "sense"),
        "witness": sum(1 for a in agents if a["cohort"] == "witness"),
        "frame": sum(1 for a in agents if a["cohort"] == "frame"),
        "understand": sum(1 for a in agents if a["cohort"] == "understand"),
        "stream": sum(1 for a in agents if a["cohort"] == "stream")
    },
    "governance_chain": ["prompts", "protocols", "bracket_protocols", "swfus_kpgs", "cloud_hood"],
    "agents": agents
}

path = r"c:\Users\rkhol\OneDrive\Documents\Anthropic\Introduction to MCP\docs\swarm-ops\agents\KPGS_KHELOS_100_AGENTS.json"
with open(path, "w", encoding="utf-8") as f:
    json.dump(catalog, f, indent=2, ensure_ascii=False)
    f.write("\n")

total = catalog["counts"]["total"]
sz = os.path.getsize(path)
print("GENERATED:", total, "agents")
print("  Sense:", catalog["counts"]["sense"])
print("  Witness:", catalog["counts"]["witness"])
print("  Frame:", catalog["counts"]["frame"])
print("  Understand:", catalog["counts"]["understand"])
print("  Stream:", catalog["counts"]["stream"])
print("  File size:", sz, "bytes")
