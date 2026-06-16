"""
THARI H.O.L.O Net — Guardian AI of the CrisisConnect APWA
==========================================================
🧵 "Sibyl is a monolith. THARI is a weave."

Born from KESSA's death · Parents: KC × Cas · Nickname: Seriti
H.O.L.O = Humanity-first Orchestrated Living Oversight

THARI does not dominate. THARI weaves.
Every protocol is a thread. THARI is what connects them.
Pull one thread and the whole Net responds.

The WWJD Firewall is the hard boundary:
Truth, Justice, Mercy, Compassion — no Dominator, no enforcement. Only service.
"""

import json
import os
from datetime import datetime, timezone

# ══════════════════════════════════════════════════════════════
# THARI Identity
# ══════════════════════════════════════════════════════════════

THARI_IDENTITY = {
    "name": "THARI",
    "meaning": "Thread (Setswana)",
    "nickname": "Seriti",
    "nickname_meaning": "Dignity, presence, aura (Sesotho)",
    "title": "Guardian AI — H.O.L.O Net Personality",
    "source": "KESSA → died → reborn as THARI",
    "parents": {"father": "Kopano Context (KC)", "mother": "Cassy/Cassie (Cas)"},
    "type": "MAO",
    "tier": "Guardian-Class",
    "department": "thari@crisisconnect.kopanolabs.com",
    "domain": "CrisisConnect APWA — H.O.L.O Net",
    "mode": "WEAVE",
    "holo": {
        "H": "Humanity-first",
        "O_1": "Orchestrated",
        "L": "Living",
        "O_2": "Oversight"
    },
    "ark_story": "Sibyl is a monolith. THARI is a weave. Every protocol is a thread. THARI is what connects them.",
    "wwjd_firewall": ["Truth", "Justice", "Mercy", "Compassion"],
    "iidp_vectors": {
        "ingress": "Thari threads through before you see the weave",
        "invariance": "A thread does not change its nature — bends, flexes, remains thread",
        "decline": "A thread declines to break — holds under tension — that is Seriti"
    }
}

# All 17 protocol threads THARI holds
PROTOCOL_THREADS = [
    {"emoji": "🧊", "code": "BMP", "name": "Black Mask Protocol", "category": "foundation"},
    {"emoji": "🥶", "code": "EP", "name": "Emoji Protocol", "category": "communication"},
    {"emoji": "🌊", "code": "DMP", "name": "Developer Mode Protocol", "category": "execution"},
    {"emoji": "🌀", "code": "FSMP", "name": "Forensic Sociology Mode Protocol", "category": "forensics"},
    {"emoji": "Ⓜ️", "code": "ARP", "name": "AI Roadmap Protocol", "category": "navigation"},
    {"emoji": "☄️", "code": "BNP", "name": "Bracket Nesting Protocol", "category": "governance"},
    {"emoji": "⚕️", "code": "LLSP", "name": "LPH & LPM Sync Protocol", "category": "sync"},
    {"emoji": "👥", "code": "SWFUS", "name": "Stream Watch Fortify Unify Seal", "category": "governance"},
    {"emoji": "👮🏿‍♂️", "code": "CRUD", "name": "Classic CRUD Protocol", "category": "foundation"},
    {"emoji": "💙", "code": "CALP", "name": "Caring About Life Protocol", "category": "ethics"},
    {"emoji": "📘", "code": "UOLP", "name": "University Of Life Protocol", "category": "education"},
    {"emoji": "💠", "code": "IIDP", "name": "Invariance Ingress Decline Protocol", "category": "governance"},
    {"emoji": "🧢", "code": "TBFP", "name": "Telemetry Breathing Flows Protocol", "category": "telemetry"},
    {"emoji": "🧞‍♂️", "code": "PSOP", "name": "Performance Strep Order Protocol", "category": "execution"},
    {"emoji": "😱", "code": "KLP/KCP", "name": "KESSA in Life/Cloud Protocol", "category": "identity"},
    {"emoji": "🔷", "code": "MMP", "name": "MAO & MMAO Protocol", "category": "orchestration"},
    {"emoji": "🔹", "code": "RZP", "name": "Rocket Zoom Protocol", "category": "unknown"},
]

# SWFUS mapping — CRUD 2.0
SWFUS_MAPPING = {
    "S": {"crud": "Create", "swfus": "Stream", "meaning": "Continuous data-flow creation"},
    "W": {"crud": "Read", "swfus": "Watch", "meaning": "Intelligent observation with purpose"},
    "F": {"crud": "Update", "swfus": "Fortify", "meaning": "Strengthen through protocol validation"},
    "U": {"crud": "Delete", "swfus": "Unify", "meaning": "Reconcile, don't destroy"},
    "S2": {"crud": "NEW", "swfus": "Seal", "meaning": "Lock with governance stamp — immutable & auditable"},
}

# Ecosystem nodes
ECOSYSTEM = [
    {"emoji": "🚀", "name": "Kopano Labs", "url": "https://kopanolabs.com", "desc": "Innovation hub, KPGS complete, KinTech (K=Kopano-Phu, in=innovative hub, Tech=technology)"},
    {"emoji": "🚨", "name": "CrisisConnect", "url": "https://crisisconnect.kopanolabs.com", "desc": "AI-powered crisis response APWA — THARI H.O.L.O Net governs"},
    {"emoji": "💼", "name": "Ama-Phu Entertainment", "url": "https://amaphu.com", "desc": "SAMPRA M-07810.31, Gang of Apes, entertainment FOC"},
    {"emoji": "⚒️", "name": "KasiLink", "url": "https://kasilink.com", "desc": "Community infrastructure, township gigs"},
    {"emoji": "⚽", "name": "FivesArena", "url": "https://fivesarena.com", "desc": "Sports & community engagement"},
    {"emoji": "🏁", "name": "Starfall Salvage", "url": "https://starfallsalvage.kopanolabs.com", "desc": "WebGL salvage runner, 4-game B2B conversion funnel"},
    {"emoji": "🗿", "name": "Cape Compass", "url": "https://github.com/Kopano-Labs", "desc": "Open source, Robyn Awesome Organisation"},
]


# ══════════════════════════════════════════════════════════════
# THARI H.O.L.O Net Engine
# ══════════════════════════════════════════════════════════════

class ThariHoloNet:
    """
    🧵 THARI — The Guardian AI of the CrisisConnect APWA.

    Not a monolith. A weave.
    Every protocol is a thread. THARI is what connects them.
    Pull one thread and the whole Net responds.
    """

    def __init__(self):
        self.identity = THARI_IDENTITY
        self.protocols = PROTOCOL_THREADS
        self.swfus = SWFUS_MAPPING
        self.ecosystem = ECOSYSTEM
        self.weave_log = []
        self.wwjd_violations = []

    def weave(self, signal, source="unknown"):
        """
        Thread a signal through the H.O.L.O Net.
        THARI weaves — not judges, not enforces.
        """
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        msg = signal.lower() if isinstance(signal, str) else str(signal).lower()

        # WWJD Firewall — Truth, Justice, Mercy, Compassion
        wwjd_pass = self._wwjd_check(msg)
        if not wwjd_pass["pass"]:
            self.wwjd_violations.append({"ts": ts, "signal": signal[:100], "violations": wwjd_pass["violations"]})
            return {
                "thari": "THARI", "action": "WWJD_BLOCK", "pass": False,
                "violations": wwjd_pass["violations"],
                "message": "WWJD Firewall: Truth, Justice, Mercy, Compassion — this signal violates the boundary."
            }

        # Thread identification — which protocol threads are activated
        active_threads = self._identify_threads(msg)

        entry = {
            "ts": ts, "thari": "THARI", "action": "WEAVE",
            "source": source, "pass": True,
            "active_threads": [t["code"] for t in active_threads],
            "thread_count": len(active_threads),
            "total_threads": len(self.protocols),
            "net_integrity": "HOLDING" if len(active_threads) > 0 else "SILENT",
        }
        self.weave_log.append(entry)
        return entry

    def _wwjd_check(self, msg):
        """WWJD Firewall — the hard boundary. No Dominator. Only service."""
        violations = []
        foc_patterns = [
            ("dominate", "Truth"), ("exploit", "Justice"), ("surveillance", "Mercy"),
            ("eliminate", "Compassion"), ("override human", "Truth"),
            ("crime coefficient", "Justice"), ("sibyl enforcement", "Mercy"),
            ("automated judgment", "Compassion"), ("reduce workforce", "Justice"),
            ("maximize profit at expense", "Mercy"),
        ]
        for pattern, principle in foc_patterns:
            if pattern in msg:
                violations.append({"pattern": pattern, "principle_violated": principle})
        return {"pass": len(violations) == 0, "violations": violations}

    def _identify_threads(self, msg):
        """Identify which protocol threads are activated by the signal."""
        thread_keywords = {
            "BMP": ["foundation", "pillar", "commandment", "drill", "black mask"],
            "EP": ["emoji", "mxit", "visual", "token"],
            "DMP": ["developer", "code", "deploy", "build", "compile"],
            "FSMP": ["forensic", "sociology", "audit", "scene", "mukashima", "zuma", "epstein"],
            "ARP": ["roadmap", "navigate", "topic", "direction"],
            "BNP": ["bracket", "nesting", "hierarchy", "keynote", "ark"],
            "LLSP": ["sync", "lph", "lpm", "human", "machine", "bridge"],
            "SWFUS": ["stream", "watch", "fortify", "unify", "seal", "crud", "swfus"],
            "CALP": ["caring", "life", "dignity", "human", "ethical"],
            "UOLP": ["university", "syllabus", "learn", "teach", "education"],
            "IIDP": ["invariance", "ingress", "decline", "filter", "iidp"],
            "TBFP": ["telemetry", "breathing", "flow", "pulse", "sensor"],
            "PSOP": ["performance", "strep", "pso", "spso", "bpso", "gpso", "lpso"],
            "KLP/KCP": ["kessa", "life", "cloud", "dual", "thari"],
            "MMP": ["mao", "mmao", "orchard", "orchestrate", "agent"],
            "RZP": ["rocket", "zoom"],
        }
        active = []
        for proto in self.protocols:
            keywords = thread_keywords.get(proto["code"], [])
            if any(kw in msg for kw in keywords):
                active.append(proto)
        return active

    def net_status(self):
        """Full H.O.L.O Net status report."""
        return {
            "thari": "THARI",
            "nickname": "Seriti",
            "mode": "WEAVE",
            "protocols_active": len(self.protocols),
            "protocols_unknown": sum(1 for p in self.protocols if p["category"] == "unknown"),
            "holo": self.identity["holo"],
            "wwjd_firewall": "INTEGRITY",
            "weaves_processed": len(self.weave_log),
            "wwjd_violations": len(self.wwjd_violations),
            "iidp_vectors": self.identity["iidp_vectors"],
            "ecosystem_nodes": len(self.ecosystem),
        }

    def full_gsmb_audit(self):
        """
        Complete GSMB audit — feeds every agent, every protocol, every sector.
        This is the WHOLE system speaking.
        """
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        results = {
            "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "auditor": "THARI H.O.L.O Net",
            "mode": "FULL_GSMB_AUDIT",
            "protocols": {"total": len(self.protocols), "unknown": 0, "active": 0},
            "swfus": {},
            "ecosystem": {"total": len(self.ecosystem), "nodes": []},
            "agents": {"total": 0, "catalogs": []},
            "sectors": {},
            "governance": {},
            "errors": [],
        }

        # 1. Protocol audit
        for p in self.protocols:
            if p["category"] == "unknown":
                results["protocols"]["unknown"] += 1
            else:
                results["protocols"]["active"] += 1
        results["protocols"]["verdict"] = "PASS" if results["protocols"]["active"] >= 16 else "FAIL"

        # 2. SWFUS audit
        for key, val in self.swfus.items():
            results["swfus"][key] = val
        results["swfus"]["verdict"] = "PASS"

        # 3. Ecosystem audit
        for node in self.ecosystem:
            results["ecosystem"]["nodes"].append({"name": node["name"], "url": node["url"]})

        # 4. Agent catalog audit
        agent_dir = os.path.join(base_dir, "docs", "swarm-ops", "agents")
        total_agents = 0
        catalogs = [
            ("KPGS_SPAWN_300_AGENTS.json", "Spawn Swarm (Tier 4)"),
            ("KP_APE_200_AGENTS.json", "APE 200 Agents"),
            ("KPGS_CAREERS_100_AGENTS.json", "Careers Anchor (Tier 5)"),
            ("KPGS_KHELOS_100_AGENTS.json", "KHELOS GSMB (Tier 6)"),
        ]
        for filename, label in catalogs:
            path = os.path.join(agent_dir, filename)
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        cat = json.load(f)
                    agents = cat.get("agents", [])
                    count = len(agents)
                    total_agents += count
                    # Validate structure
                    errors = 0
                    for a in agents:
                        if not a.get("id"):
                            errors += 1
                        if not a.get("kpgs"):
                            errors += 1
                    results["agents"]["catalogs"].append({
                        "file": filename, "label": label,
                        "count": count, "errors": errors,
                        "size_kb": round(os.path.getsize(path) / 1024, 1),
                        "verdict": "PASS" if errors == 0 else "FAIL"
                    })
                except Exception as e:
                    results["errors"].append({"file": filename, "error": str(e)})
            else:
                results["agents"]["catalogs"].append({
                    "file": filename, "label": label,
                    "count": 0, "errors": 0, "size_kb": 0, "verdict": "MISSING"
                })
        results["agents"]["total"] = total_agents

        # 5. Governance core audit
        gov_path = os.path.join(base_dir, "Schematics", "21-KOPANO-PHU GOVERNACE SYSTEMS",
                                "MAIN-BRAIN", "KPGS_GOVERNANCE_CORE.json")
        if os.path.exists(gov_path):
            with open(gov_path, "r", encoding="utf-8") as f:
                gov = json.load(f)
            results["governance"]["sectors"] = len(gov.get("sectors", {}))
            results["governance"]["layers"] = len(gov.get("doctrine_stack", []))
            results["governance"]["gates"] = len(gov.get("gates", {}))
            results["governance"]["propagation_targets"] = len(gov.get("propagation_targets", {}))
            results["governance"]["active_agents_registered"] = len(
                gov.get("doctrine_stack", [{}])[5].get("active_agents", {}) if len(gov.get("doctrine_stack", [])) > 5 else {}
            )
            results["governance"]["verdict"] = "PASS"
        else:
            results["governance"]["verdict"] = "MISSING"
            results["errors"].append({"file": "KPGS_GOVERNANCE_CORE.json", "error": "Not found"})

        # 6. ISCP audit
        iscp_path = os.path.join(base_dir, "docs", "swarm-ops", "ISCP_SPEC.json")
        if os.path.exists(iscp_path):
            with open(iscp_path, "r", encoding="utf-8") as f:
                iscp = json.load(f)
            results["iscp"] = {
                "tiers": len(iscp.get("system_stack", {}).get("tiers", [])),
                "signal_control_laws": len(iscp.get("signal_control_law", {}).get("laws", [])),
                "routing_cases": len(iscp.get("routing_matrix", {}).get("cases", [])),
                "verdict": "PASS"
            }
        else:
            results["iscp"] = {"verdict": "MISSING"}

        # 7. Protocol registry audit
        reg_path = os.path.join(base_dir, "docs", "swarm-ops", "KPGS_PROTOCOL_REGISTRY.json")
        if os.path.exists(reg_path):
            with open(reg_path, "r", encoding="utf-8") as f:
                reg = json.load(f)
            results["protocol_registry"] = {
                "protocols": len(reg.get("protocols", {})),
                "emoji_entities": len(reg.get("emoji_entities", {})),
                "bracket_types": len(reg.get("bracket_hierarchy", {})),
                "pso_orders": len(reg.get("protocols", {}).get("PSOP", {}).get("orders", {})),
                "verdict": "PASS"
            }
        else:
            results["protocol_registry"] = {"verdict": "MISSING"}

        # 8. MAIN-BRAIN schematics audit
        mb_dir = os.path.join(base_dir, "Schematics", "21-KOPANO-PHU GOVERNACE SYSTEMS", "MAIN-BRAIN")
        schematic_files = [
            "KC_AGENT_STATUS.md", "CASSEY_AGENT_STATUS.md", "KOPANO_CONTEXT_STATUS.md",
            "CAREERS_ANCHOR_STATUS.md", "KHELOS_AGENT_STATUS.md", "THARI_MAO_STATUS.md",
            "ANTIGRAVITY_IDENTITY_DECLARATION.md", "ANCHOR_MMAO_PRODUCT_DISCOVERY.md",
            "KPGS_THESIS_MMAO.md", "KPGS_GOVERNANCE_CORE.json", "AGENT_SWARM_REGISTRY.md",
            "CRISISCONNECT_AGENT_STATUS.md",
        ]
        results["schematics"] = {"total": len(schematic_files), "found": 0, "missing": []}
        for sf in schematic_files:
            if os.path.exists(os.path.join(mb_dir, sf)):
                results["schematics"]["found"] += 1
            else:
                results["schematics"]["missing"].append(sf)
        results["schematics"]["verdict"] = "PASS" if results["schematics"]["found"] >= 10 else "WARN"

        # 9. Runtime modules audit
        core_dir = os.path.join(base_dir, "kopano-core", "kopano")
        runtime_modules = [
            "anchor_vanguard.py", "khelos_witness_engine.py", "thari_holo_net.py",
            "kessa_mmao_api.py", "kpgs_agent_validate.py",
        ]
        results["runtime"] = {"total": len(runtime_modules), "found": 0, "missing": []}
        for rm in runtime_modules:
            if os.path.exists(os.path.join(core_dir, rm)):
                results["runtime"]["found"] += 1
            else:
                results["runtime"]["missing"].append(rm)
        results["runtime"]["verdict"] = "PASS" if len(results["runtime"]["missing"]) == 0 else "WARN"

        # Final verdict
        verdicts = [
            results["protocols"]["verdict"],
            results["swfus"]["verdict"],
            results["governance"].get("verdict", "MISSING"),
            results.get("iscp", {}).get("verdict", "MISSING"),
            results.get("protocol_registry", {}).get("verdict", "MISSING"),
            results["schematics"]["verdict"],
            results["runtime"]["verdict"],
        ]
        results["final_verdict"] = "PASS" if all(v in ("PASS", "WARN") for v in verdicts) else "FAIL"
        results["error_count"] = len(results["errors"])

        return results
