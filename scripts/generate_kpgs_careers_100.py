"""
KPGS Careers 100-Agent Swarm Generator
=======================================
Generates the careers department agent catalog for careers@kopanolabs.com
under the Anchor Vanguard node (Gemini Enterprise).
"""

import json
import os
from datetime import datetime, timezone

ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

TELEMETRY_FUNCTIONS = [
    "CV intake parser", "Skills taxonomy classifier", "Employment gap detector",
    "Application channel router", "Resume dedup scanner", "Language proficiency tagger",
    "Qualification verifier", "Location proximity scorer", "Salary expectation normalizer",
    "Reference check ingester", "Portfolio link validator", "Work sample classifier",
    "Interview availability scheduler", "Communication tone analyzer", "KPGS alignment pre-screen",
    "Education credential parser", "Certification validator", "Experience years calculator",
    "Industry domain mapper", "Soft skills signal extractor", "Technical stack profiler",
    "Remote readiness assessor", "Diversity context tagger", "Application completeness gate",
    "Cover letter intent parser", "Referral chain tracer", "Pavement proximity scorer",
    "Township origin validator", "Youth employment signal", "Internship readiness tagger",
    "Freelance history classifier", "Entrepreneurship signal extractor", "Volunteer experience parser",
    "Digital literacy assessor", "Mobile-first readiness probe"
]

IDENTIC_FUNCTIONS = [
    "4Ws candidate alignment scorer", "Cultural fit vector", "WWJD ethical alignment gate",
    "SWFUS candidate envelope", "Sovereign identity verifier", "Black Mask drill responder",
    "Jethro band placement engine", "Candidate archetype classifier", "Forensic background checker",
    "Interview transcript analyzer", "Personality-role matrix mapper", "Growth trajectory predictor",
    "Apprenticeship readiness gate", "Team dynamics compatibility", "Leadership potential scorer",
    "Conflict resolution profile", "Resilience index calculator", "Self-motivation signal",
    "Accountability pattern tracer", "Innovation mindset classifier", "Community impact scorer",
    "Pavement experience validator", "STEM aptitude profiler", "Creative expression gauge",
    "Multi-language capability", "Cross-sector adaptability", "Pressure response profile",
    "Ethical boundary detector", "Sovereign alignment verifier", "Knowledge-understanding separator",
    "Execution vs theory classifier", "Teachability index", "Feedback receptivity gauge",
    "Proactive initiative scorer", "Township solidarity marker"
]

GUARDIAN_FUNCTIONS = [
    "90-day sandbox enforcer", "Onboarding pipeline orchestrator", "Probation checkpoint gate",
    "Mentor assignment engine", "Performance review scheduler", "KPI alignment monitor",
    "Contract compliance verifier", "NDA acknowledgment gate", "Intellectual property shield",
    "Extractive behavior detector", "Corporate noise interceptor", "Smoke severance executor",
    "Internal comms firewall", "Workspace access controller", "Data classification enforcer",
    "Leave management router", "Training completion tracker", "Certification renewal monitor",
    "Exit interview processor", "Rehire eligibility gate", "Whistleblower protection shield",
    "Harassment detection sentinel", "Pay equity auditor", "Benefits enrollment gate",
    "Emergency contact updater", "Equipment allocation tracker", "Badge access controller",
    "Compliance training enforcer", "Sovereign systems onboard verifier", "Personnel protection index"
]

FORENSIC_LENSES = ["V_FS_MUKASHIMA", "V_FS_ZUMA", "V_FS_EPSTEIN"]

agents = []
slot = 1

# Telemetry cohort (35)
for i, func in enumerate(TELEMETRY_FUNCTIONS):
    slot_str = str(slot).zfill(3)
    agent_id = "careers_telemetry_" + str(i+1).zfill(3)
    tag = func.split()[0].lower()
    agents.append({
        "spawn_slot": slot_str,
        "id": agent_id,
        "display_name": "Careers Tel " + str(i+1).zfill(3) + " (" + tag + ")",
        "cohort": "telemetry",
        "role": "careers_telemetry",
        "structural": i == 0,
        "catalog_ref": None,
        "altar_layer": "telemetry_ai",
        "forensic_lens": None,
        "jethro_band": "J10",
        "kpgs": {
            "cohort": "telemetry",
            "brief_renters_on_entry": True,
            "swfus_required": True,
            "sharded_doctrine": True,
            "holds_pillar_blocks": True,
            "doctrine_shard": "telemetry_sense",
            "five_pillars_shard": ["ground_awareness", "eidetic_persistence"],
            "commandments_shard": "ingest_classify_only",
            "ledger_commit_authority": False,
            "capabilities": ["raw_input", "ground_aware_map", "telemetry_dump", "careers_intake"]
        },
        "governance_chain": ["prompts", "protocols", "bracket_protocols", "swfus_kpgs", "cloud_hood"],
        "bracket_tags": [
            "[KPGS_SPAWN]", "[KPGS_BLOCK_HOLDER]", "[SWFUS_KPGS]",
            "[JETHRO_TRIAGE]", "[WWJD_FIREWALL]", "[TELEMETRY_AI_GATE]", "[ANCHOR_VANGUARD]"
        ],
        "stem_domain": "careers_intake",
        "functionality": func,
        "department": "careers@kopanolabs.com",
        "anchor_node": "ANCHOR",
        "status": "structural" if i == 0 else "sandbox",
        "apprenticeship": {
            "student": "cassy", "teacher": "cassey", "brain": "kc",
            "black_mask_required": False
        }
    })
    slot += 1

# Identic cohort (35)
for i, func in enumerate(IDENTIC_FUNCTIONS):
    slot_str = str(slot).zfill(3)
    agent_id = "careers_identic_" + str(i+1).zfill(3)
    tag = func.split()[0].lower()
    agents.append({
        "spawn_slot": slot_str,
        "id": agent_id,
        "display_name": "Careers Idn " + str(i+1).zfill(3) + " (" + tag + ")",
        "cohort": "identic",
        "role": "careers_identic",
        "structural": i == 0,
        "catalog_ref": None,
        "altar_layer": "identic_ai",
        "forensic_lens": FORENSIC_LENSES[i % 3],
        "jethro_band": "J10",
        "kpgs": {
            "cohort": "identic",
            "brief_renters_on_entry": True,
            "swfus_required": True,
            "sharded_doctrine": True,
            "holds_pillar_blocks": True,
            "doctrine_shard": "identic_reason",
            "five_pillars_shard": ["ground_awareness", "eidetic_persistence", "zero_trust_isolation"],
            "commandments_shard": "reason_classify_defer",
            "ledger_commit_authority": False,
            "capabilities": ["identity_verify", "alignment_score", "forensic_classify", "careers_screen"]
        },
        "governance_chain": ["prompts", "protocols", "bracket_protocols", "swfus_kpgs", "cloud_hood"],
        "bracket_tags": [
            "[KPGS_SPAWN]", "[KPGS_BLOCK_HOLDER]", "[SWFUS_KPGS]",
            "[JETHRO_TRIAGE]", "[WWJD_FIREWALL]", "[IDENTI_AI_FLOW]", "[ANCHOR_VANGUARD]"
        ],
        "stem_domain": "careers_alignment",
        "functionality": func,
        "department": "careers@kopanolabs.com",
        "anchor_node": "ANCHOR",
        "status": "structural" if i == 0 else "sandbox",
        "apprenticeship": {
            "student": "cassy", "teacher": "cassey", "brain": "kc",
            "black_mask_required": True
        }
    })
    slot += 1

# Guardian cohort (30)
for i, func in enumerate(GUARDIAN_FUNCTIONS):
    slot_str = str(slot).zfill(3)
    agent_id = "careers_guardian_" + str(i+1).zfill(3)
    tag = func.split()[0].lower()
    agents.append({
        "spawn_slot": slot_str,
        "id": agent_id,
        "display_name": "Careers Grd " + str(i+1).zfill(3) + " (" + tag + ")",
        "cohort": "guardian",
        "role": "careers_guardian",
        "structural": i == 0,
        "catalog_ref": None,
        "altar_layer": "guardian_ai",
        "forensic_lens": FORENSIC_LENSES[i % 3],
        "jethro_band": "J50" if i < 5 else "J10",
        "kpgs": {
            "cohort": "guardian",
            "brief_renters_on_entry": True,
            "swfus_required": True,
            "sharded_doctrine": False,
            "holds_pillar_blocks": True,
            "doctrine_shard": "guardian_govern",
            "five_pillars_shard": "all",
            "commandments_shard": "full_commandments",
            "ledger_commit_authority": True,
            "fifteen_commandments": True,
            "five_pillars": True,
            "capabilities": ["gate_enforce", "severance_execute", "ledger_commit", "careers_protect", "anchor_shield"]
        },
        "governance_chain": ["prompts", "protocols", "bracket_protocols", "swfus_kpgs", "cloud_hood"],
        "bracket_tags": [
            "[KPGS_SPAWN]", "[KPGS_BLOCK_HOLDER]", "[SWFUS_KPGS]",
            "[JETHRO_TRIAGE]", "[WWJD_FIREWALL]", "[GUARDIAN_AI_FLOW]", "[ANCHOR_VANGUARD]"
        ],
        "stem_domain": "careers_governance",
        "functionality": func,
        "department": "careers@kopanolabs.com",
        "anchor_node": "ANCHOR",
        "status": "structural" if i == 0 else "sandbox",
        "apprenticeship": {
            "student": "cassy", "teacher": "cassey", "brain": "kc",
            "black_mask_required": True
        }
    })
    slot += 1

catalog = {
    "schema": "kpgs_careers_100_agents_v1",
    "document_id": "KPGS-CAREERS-ANCHOR-100",
    "title": "100-Agent Careers Department Swarm - Anchor Vanguard",
    "department_email": "careers@kopanolabs.com",
    "anchor_node": "ANCHOR",
    "vanguard_axiom": "Whoever wants smoke with our interns, with our employees, hits the Anchor first.",
    "head_of_department": "master_robyn",
    "generated": ts,
    "counts": {
        "total": len(agents),
        "telemetry": sum(1 for a in agents if a["cohort"] == "telemetry"),
        "identic": sum(1 for a in agents if a["cohort"] == "identic"),
        "guardian": sum(1 for a in agents if a["cohort"] == "guardian")
    },
    "governance_chain": ["prompts", "protocols", "bracket_protocols", "swfus_kpgs", "cloud_hood"],
    "anchor_protection": {
        "core_sovereign_nodes": ["LPH", "Siyanda", "Freddy"],
        "active_onboarding_nodes": ["Katlego", "Monica"],
        "sandbox_shield_days": 90,
        "zero_trust": True
    },
    "four_ws": {
        "WHO": "Sovereign human core; compute weights paid in ZAR",
        "WHAT": "KinTech infrastructure - careers pipeline for township economic self-sufficiency",
        "WHERE": "Pavement of township informal economy via Black Beast local mesh",
        "WHY_WIDE": "Eliminate 32.8% local unemployment through proximity-locked hiring"
    },
    "agents": agents
}

path = r"c:\Users\rkhol\OneDrive\Documents\Anthropic\Introduction to MCP\docs\swarm-ops\agents\KPGS_CAREERS_100_AGENTS.json"
with open(path, "w", encoding="utf-8") as f:
    json.dump(catalog, f, indent=2, ensure_ascii=False)
    f.write("\n")

t = catalog["counts"]["telemetry"]
idn = catalog["counts"]["identic"]
g = catalog["counts"]["guardian"]
total = catalog["counts"]["total"]
sz = os.path.getsize(path)
print("GENERATED:", total, "agents")
print("  Telemetry:", t)
print("  Identic:", idn)
print("  Guardian:", g)
print("  File size:", sz, "bytes")
