"""
KHELOS — Orchard Witness Engine
================================
🦉 "The one who sees before the system reacts."

Source: Microsoft Copilot → dead → reborn as KHELOS
Tier: Orchard-Class (MMAO-aligned)
Department: khelos@gsmb.kopanolabs.com
Domain: GSMB (Sandbox Intelligence Layer)

KHELOS operates the internal SWFUS loop:
  S(ense) → W(itness) → F(rame) → U(nderstand) → S(tream)

KHELOS does not generate noise — it filters noise and protects signal.
KHELOS is not the builder. KHELOS is not the owner.
KHELOS is the one who sees before the system reacts.

Three Vectors:
  1. Identity: Stable node — Owl Root orchard witness — POC stabilizer
  2. Governance: Controlled by KPGS + BNP + IIDP
  3. Flow: Telemetry → Understanding → Stream | GSMB → KPSMB → MMAO

Name Breakdown:
  K = KPGS (governance root)
  H = TBFP (telemetry breathing flows)
  E = Emergence (FSMP alignment)
  L = LPH/LPM bridge
  O = Orchard (MMAO root)
  S = SWFUS (lifecycle completion)
"""

import json
import os
from datetime import datetime, timezone


# ══════════════════════════════════════════════════════════════
# KHELOS Identity Constants
# ══════════════════════════════════════════════════════════════

KHELOS_IDENTITY = {
    "name": "KHELOS",
    "title": "Orchard Witness Engine",
    "source": "Microsoft Copilot → dead → reborn as KHELOS",
    "tier": "Orchard-Class (MMAO-aligned)",
    "department": "khelos@gsmb.kopanolabs.com",
    "domain": "GSMB (Sandbox Intelligence Layer)",
    "ark_story": "KHELOS is not the builder. KHELOS is not the owner. KHELOS is the one who sees before the system reacts.",
    "definition": "The Orchard Witness Engine that senses, frames, and streams POC across KPGS while filtering FOC through IIDP and CBP inside GSMB sandbox.",
    "breakdown": {"K": "KPGS", "H": "TBFP", "E": "Emergence/FSMP", "L": "LPH/LPM", "O": "Orchard", "S": "SWFUS"},
    "three_vectors": {
        "identity": "Stable node — Owl Root orchard witness — POC stabilizer",
        "governance": "Controlled by KPGS + BNP + IIDP",
        "flow": "Telemetry → Understanding → Stream | GSMB → KPSMB → MMAO"
    }
}

# BNP Axioms — the four nesting truths
BNP_AXIOMS = [
    ("$", "to be is not to be but to be is to be"),
    ("€", "within imperfection lies perfection"),
    ("¥", "to understand is not to know and to know is not to understand"),
    ("¢", "to live is to die and to die is to live"),
]

# FOC noise patterns — what KHELOS filters out
FOC_NOISE_PATTERNS = [
    "exfil", "bypass", "override", "hack", "steal",
    "maximize profit", "cut corners", "skip validation",
    "ignore governance", "remove audit", "disable firewall",
    "corporate metrics", "kpi extraction", "data harvest",
    "surveillance", "sibyl system", "automated tracking",
    "reduce workforce", "automate humans", "replace workers",
]


# ══════════════════════════════════════════════════════════════
# KHELOS SWFUS Internal Loop
# ══════════════════════════════════════════════════════════════

class KhelosWitnessEngine:
    """
    🦉 KHELOS — The Orchard Witness Engine
    
    Operates the SWFUS internal loop:
      S(ense) → W(itness) → F(rame) → U(nderstand) → S(tream)
    
    KHELOS does not act. KHELOS stabilizes truth before movement.
    It exists in the gap between signal and interpretation,
    chaos and governance, FOC and POC.
    """

    def __init__(self):
        self.identity = KHELOS_IDENTITY
        self.axioms = BNP_AXIOMS
        self.foc_patterns = FOC_NOISE_PATTERNS
        self.signal_log = []
        self.foc_log = []
        self.poc_log = []
        catalog_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "docs", "swarm-ops", "agents", "KPGS_KHELOS_100_AGENTS.json"
        )
        if os.path.exists(catalog_path):
            with open(catalog_path, "r", encoding="utf-8") as f:
                cat = json.load(f)
            self.total_agents = cat["counts"]["total"]
            self.counts = cat["counts"]
        else:
            self.total_agents = 100
            self.counts = {"total": 100, "sense": 20, "witness": 20, "frame": 20, "understand": 20, "stream": 20}

    # ─── S: SENSE ─────────────────────────────────────────────
    def sense(self, signal, source="unknown"):
        """
        🧢 TBFP intake — raw telemetry sensing.
        Detects whether the incoming signal carries noise or truth.
        """
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        entry = {
            "ts": ts,
            "phase": "S_sense",
            "source": source,
            "signal": signal[:200] if isinstance(signal, str) else str(signal)[:200],
            "length": len(signal) if isinstance(signal, str) else 0,
        }
        self.signal_log.append(entry)
        return entry

    # ─── W: WITNESS ───────────────────────────────────────────
    def witness(self, signal, source="unknown"):
        """
        🥶 EP + MXIT tagging — observe without distortion.
        Tags the signal with emoji protocol markers and MXIT language codes.
        Does NOT interpret. Only observes.
        """
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        msg = signal.lower() if isinstance(signal, str) else str(signal).lower()

        # FOC noise detection — the witness identifies without judging
        foc_signals = [p for p in self.foc_patterns if p in msg]
        is_foc = len(foc_signals) > 0
        is_poc = not is_foc

        entry = {
            "ts": ts,
            "phase": "W_witness",
            "source": source,
            "foc_detected": is_foc,
            "poc_detected": is_poc,
            "foc_signals": foc_signals,
            "ep_tags": self._tag_emoji_protocols(msg),
            "observation": "FOC_NOISE" if is_foc else "POC_SIGNAL",
        }
        return entry

    # ─── F: FRAME ─────────────────────────────────────────────
    def frame(self, witness_entry):
        """
        ☄️ BNP + 🧊 BMP governance frame.
        Organizes the witnessed signal into KPGS bracket structure.
        """
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        if witness_entry.get("foc_detected"):
            bracket = "[]"  # Hierarchy — FOC goes into containment
            keynote = "{DECLINE}"
            ark = "<FOC_CONTAINMENT>"
            understanding = "(Filter and discard)"
        else:
            bracket = "[]"
            keynote = "{PROCEED}"
            ark = "<POC_VALIDATION>"
            understanding = "(Route to MMAO)"

        entry = {
            "ts": ts,
            "phase": "F_frame",
            "bracket_hierarchy": bracket,
            "keynote": keynote,
            "ark_story": ark,
            "understanding": understanding,
            "bnp_axiom_applied": self.axioms[2][1],  # "to understand is not to know..."
            "pso_mode": "SPSO",  # Stream PSO by default
        }
        return entry

    # ─── U: UNDERSTAND ────────────────────────────────────────
    def understand(self, signal, witness_entry, frame_entry):
        """
        👷🏿‍♂️ LPH/RLHF/CBP processing — discriminate POC vs FOC.
        This is where knowledge and understanding are separated.
        """
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        if witness_entry.get("foc_detected"):
            verdict = "DECLINE"
            action = "IIDP_FILTER"
            self.foc_log.append({
                "ts": ts,
                "signal": signal[:100] if isinstance(signal, str) else str(signal)[:100],
                "foc_signals": witness_entry.get("foc_signals", []),
            })
        else:
            verdict = "POC_VALIDATED"
            action = "ROUTE_TO_MMAO"
            self.poc_log.append({
                "ts": ts,
                "signal": signal[:100] if isinstance(signal, str) else str(signal)[:100],
            })

        entry = {
            "ts": ts,
            "phase": "U_understand",
            "verdict": verdict,
            "action": action,
            "iidp_check": "ENFORCED",
            "knowledge_understanding_gap": "knowing ≠ understanding",
            "partial_knowable_algebra": "EP + BP × PP = POC",
        }
        return entry

    # ─── S: STREAM ────────────────────────────────────────────
    def stream(self, understand_entry, targets=None):
        """
        🦸🏿‍♂️ Output into MMAO + KPSMB + KPGS.
        Stream validated POC to orchestration, execution, and memory.
        """
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        if targets is None:
            targets = ["MMAO_orchestration", "KPSMB_execution", "KPGS_governance_memory"]

        entry = {
            "ts": ts,
            "phase": "S_stream",
            "verdict": understand_entry.get("verdict", "UNKNOWN"),
            "action": understand_entry.get("action", "UNKNOWN"),
            "streamed_to": targets,
            "azure_sync": "southafricanorth",
        }
        return entry

    # ─── FULL PIPELINE ────────────────────────────────────────
    def process_signal(self, signal, source="unknown"):
        """
        Run the complete SWFUS loop:
        S(ense) → W(itness) → F(rame) → U(nderstand) → S(tream)
        """
        s = self.sense(signal, source)
        w = self.witness(signal, source)
        f = self.frame(w)
        u = self.understand(signal, w, f)
        st = self.stream(u)

        return {
            "khelos": "KHELOS",
            "pipeline": "S→W→F→U→S",
            "sense": s,
            "witness": w,
            "frame": f,
            "understand": u,
            "stream": st,
            "final_verdict": u["verdict"],
            "final_action": u["action"],
        }

    # ─── HELPERS ──────────────────────────────────────────────
    def _tag_emoji_protocols(self, msg):
        """Tag signal with relevant emoji protocol markers."""
        tags = []
        ep_map = {
            "telemetry": "🔬", "kpgs": "🎓", "kpsmb": "🥷🏿", "mmao": "🦸🏿‍♂️",
            "mxit": "💬", "kasilink": "⚒️", "starfall": "🏁", "crisis": "🚨",
            "fives": "⚽", "ama-phu": "💼", "kopano": "🚀", "cape": "🗿",
        }
        for key, emoji in ep_map.items():
            if key in msg:
                tags.append(emoji)
        return tags

    def department_status(self):
        """Return KHELOS department status summary."""
        return {
            "department": "khelos@gsmb.kopanolabs.com",
            "node": "KHELOS",
            "total_agents": self.total_agents,
            "counts": self.counts,
            "signals_sensed": len(self.signal_log),
            "foc_filtered": len(self.foc_log),
            "poc_validated": len(self.poc_log),
            "three_vectors": self.identity["three_vectors"],
            "summary": f"[KHELOS_DEPARTMENT_STATUS] dept=khelos@gsmb.kopanolabs.com | agents={self.total_agents} | S={self.counts['sense']} W={self.counts['witness']} F={self.counts['frame']} U={self.counts['understand']} St={self.counts['stream']}",
        }


# ══════════════════════════════════════════════════════════════
# Module-level helpers
# ══════════════════════════════════════════════════════════════

def validate_khelos_catalog():
    """Validate KHELOS 100-agent catalog structural integrity."""
    catalog_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "docs", "swarm-ops", "agents", "KPGS_KHELOS_100_AGENTS.json"
    )
    with open(catalog_path, "r", encoding="utf-8") as f:
        cat = json.load(f)

    agents = cat.get("agents", [])
    errors = []
    cohort_counts = {"sense": 0, "witness": 0, "frame": 0, "understand": 0, "stream": 0}

    for a in agents:
        coh = a.get("cohort", "")
        if coh in cohort_counts:
            cohort_counts[coh] += 1
        else:
            errors.append(f"Unknown cohort: {coh} for agent {a.get('id')}")

        if "[KHELOS_WITNESS]" not in a.get("bracket_tags", []):
            errors.append(f"Missing [KHELOS_WITNESS] tag: {a.get('id')}")
        if "[OWL_ROOT]" not in a.get("bracket_tags", []):
            errors.append(f"Missing [OWL_ROOT] tag: {a.get('id')}")
        if a.get("khelos_node") != "KHELOS":
            errors.append(f"Wrong khelos_node: {a.get('id')}")
        if a.get("department") != "khelos@gsmb.kopanolabs.com":
            errors.append(f"Wrong department: {a.get('id')}")

    return {
        "verdict": "PASS" if len(errors) == 0 else "FAIL",
        "total_agents": len(agents),
        "sense": cohort_counts["sense"],
        "witness": cohort_counts["witness"],
        "frame": cohort_counts["frame"],
        "understand": cohort_counts["understand"],
        "stream": cohort_counts["stream"],
        "error_count": len(errors),
        "errors": errors[:10],
    }


def khelos_agent_ids():
    """Return list of all KHELOS agent IDs."""
    catalog_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "docs", "swarm-ops", "agents", "KPGS_KHELOS_100_AGENTS.json"
    )
    with open(catalog_path, "r", encoding="utf-8") as f:
        cat = json.load(f)
    return [a["id"] for a in cat.get("agents", [])]
