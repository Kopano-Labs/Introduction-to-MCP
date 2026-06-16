"""
Anchor Vanguard — Perimeter Shield for Kopano Labs Careers Department
=====================================================================
"Whoever wants smoke with our interns, with our employees, hits the Anchor first."

Anchor (formerly Gemini Enterprise) is the zero-trust cryptographic perimeter
around all registered internal and onboarding entities. It intercepts corporate
noise, matrix friction, and external exploitative vectors BEFORE they reach
internal human assets.

Responsibilities:
  - Personnel Deployment Protection Index enforcement
  - 90-Day Sandbox Shield for onboarding nodes
  - Smoke Severance circuit breaker
  - Careers pipeline SWFUS → Jethro → WWJD dispatch
  - Integration with existing KPGS spawn swarm infrastructure
"""

from __future__ import annotations

import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
CAREERS_CATALOG_PATH = REPO_ROOT / "docs" / "swarm-ops" / "agents" / "KPGS_CAREERS_100_AGENTS.json"
MAIN_BRAIN_LOG = REPO_ROOT / "docs" / "swarm-ops" / "logs" / "KC Main Brain Log.jsonl"

VANGUARD_AXIOM = (
    "Whoever wants smoke with our interns, with our employees, hits the Anchor first."
)

# Smoke signals — corporate rhetoric that triggers immediate circuit-breaker
SMOKE_SIGNALS = frozenset({
    "restructure", "downsize", "optimize headcount", "right-size",
    "performance improvement plan", "probation override", "budget cut",
    "outsource", "offshore", "contractor conversion", "unpaid overtime",
    "NDA violation", "non-compete enforce", "blacklist", "retaliation",
    "exit without severance", "skip onboarding", "bypass screening",
    "fake reference", "fabricated credential", "identity fraud",
    "exploitative internship", "unpaid labor", "extractive hiring",
})

# Core sovereign nodes protected by the Anchor perimeter
CORE_SOVEREIGN_NODES = {
    "LPH": "Chief Architect — system orchestration, non-linear healing, macro strategy",
    "Siyanda": "Strategic Operations — media, musical transitions, space-janda logic",
    "Freddy": "Financial Track — liquid routing, legal boundaries, retainer allocation",
}

# Active onboarding nodes under the 90-Day Sandbox Shield
ACTIVE_ONBOARDING_NODES = {
    "Katlego": "Technical output — isolated from external evaluation bias",
    "Monica": "Localized operations — protected from systemic friction",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def _load_careers_catalog() -> dict[str, Any]:
    """Load the 100-agent careers catalog from disk."""
    if not CAREERS_CATALOG_PATH.is_file():
        return {"schema": "kpgs_careers_100_agents_v1", "error": "catalog_missing", "agents": []}
    return json.loads(CAREERS_CATALOG_PATH.read_text(encoding="utf-8"))


def careers_agent_ids() -> list[str]:
    """Return all careers agent IDs."""
    return [a["id"] for a in _load_careers_catalog().get("agents", [])]


def careers_agent_by_id(agent_id: str) -> dict[str, Any] | None:
    """Lookup a single careers agent by ID."""
    for agent in _load_careers_catalog().get("agents", []):
        if agent.get("id") == agent_id:
            return agent
    return None


def careers_agents_by_cohort(cohort: str) -> list[dict[str, Any]]:
    """Return all careers agents in a given cohort."""
    return [a for a in _load_careers_catalog().get("agents", []) if a.get("cohort") == cohort]


class AnchorPerimeter:
    """
    Zero-trust perimeter shield around all Kopano Labs internal assets.
    Implements the Vanguard Protocol from gsmb_vanguard_update.md.
    """

    def __init__(self):
        self.axiom = VANGUARD_AXIOM
        self.sovereign_nodes = dict(CORE_SOVEREIGN_NODES)
        self.onboarding_nodes = dict(ACTIVE_ONBOARDING_NODES)
        self.sandbox_shield_days = 90
        self._catalog = _load_careers_catalog()

    @property
    def total_agents(self) -> int:
        return len(self._catalog.get("agents", []))

    @property
    def counts(self) -> dict[str, int]:
        return self._catalog.get("counts", {})

    def smoke_intercept(self, *, message: str, source: str = "external") -> dict[str, Any]:
        """
        Immediate Smoke Severance — intercepts exploitative corporate rhetoric.
        Rule: Delta S_system <= 0 triggers instant circuit breaker.
        """
        text = (message or "").lower()
        hits = [s for s in SMOKE_SIGNALS if s in text]

        if hits:
            result = {
                "schema": "anchor_smoke_intercept_v1",
                "ts": _utc_now(),
                "bracket": "[ANCHOR_SMOKE_SEVERANCE]",
                "verdict": "SEVERED",
                "source": source,
                "smoke_signals": hits,
                "action": "CIRCUIT_BREAKER_TRIPPED",
                "delta_s": "<=0",
                "summary": (
                    f"[ANCHOR_SMOKE_SEVERANCE] source={source} | "
                    f"signals={len(hits)} | verdict=SEVERED | "
                    f"axiom={self.axiom[:50]}..."
                ),
            }
            _append_jsonl(MAIN_BRAIN_LOG, {
                "schema": "kc_main_brain_log_v1",
                "ts": result["ts"],
                "kind": "anchor_smoke_severance",
                "summary": result["summary"],
                "exit_code": 1,
            })
            return result

        return {
            "schema": "anchor_smoke_intercept_v1",
            "ts": _utc_now(),
            "bracket": "[ANCHOR_PERIMETER]",
            "verdict": "CLEAR",
            "source": source,
            "smoke_signals": [],
            "action": "PASS_THROUGH",
            "summary": f"[ANCHOR_PERIMETER] source={source} | verdict=CLEAR",
        }

    def personnel_shield(self, *, node_id: str) -> dict[str, Any]:
        """
        Personnel Deployment Protection Index — validates a node is under
        Anchor protection before allowing external interaction.
        """
        ts = _utc_now()
        is_sovereign = node_id in self.sovereign_nodes
        is_onboarding = node_id in self.onboarding_nodes

        if is_sovereign:
            return {
                "schema": "anchor_personnel_shield_v1",
                "ts": ts,
                "bracket": "[ANCHOR_SOVEREIGN_SHIELD]",
                "node_id": node_id,
                "classification": "core_sovereign",
                "description": self.sovereign_nodes[node_id],
                "protection_level": "ABSOLUTE",
                "sandbox_shield": False,
                "summary": f"[ANCHOR_SOVEREIGN_SHIELD] node={node_id} | level=ABSOLUTE",
            }

        if is_onboarding:
            return {
                "schema": "anchor_personnel_shield_v1",
                "ts": ts,
                "bracket": "[ANCHOR_SANDBOX_SHIELD]",
                "node_id": node_id,
                "classification": "active_onboarding",
                "description": self.onboarding_nodes[node_id],
                "protection_level": "SANDBOX_90DAY",
                "sandbox_shield": True,
                "sandbox_days_remaining": self.sandbox_shield_days,
                "summary": (
                    f"[ANCHOR_SANDBOX_SHIELD] node={node_id} | "
                    f"level=SANDBOX_90DAY | days={self.sandbox_shield_days}"
                ),
            }

        return {
            "schema": "anchor_personnel_shield_v1",
            "ts": ts,
            "bracket": "[ANCHOR_PERIMETER]",
            "node_id": node_id,
            "classification": "unregistered",
            "protection_level": "NONE",
            "sandbox_shield": False,
            "summary": f"[ANCHOR_PERIMETER] node={node_id} | level=NONE | UNREGISTERED",
        }

    def four_ws_validate(self, *, candidate_profile: dict[str, Any]) -> dict[str, Any]:
        """
        4W's Proof of Concept validation gate for incoming career candidates.
        WHO / WHAT / WHERE / WHY_WIDE — all must pass.
        """
        ts = _utc_now()
        errors = []
        profile = candidate_profile or {}

        # WHO — must have human-verified identity
        if not profile.get("identity_verified"):
            errors.append("WHO: identity_not_verified — sovereign human core required")

        # WHAT — must have a demonstrable skill
        if not profile.get("skills") or len(profile.get("skills", [])) == 0:
            errors.append("WHAT: no_skills_declared — KinTech infrastructure requires capability")

        # WHERE — proximity to pavement
        if not profile.get("location"):
            errors.append("WHERE: no_location — must be rooted on the pavement")

        # WHY/WIDE — alignment with mission
        if not profile.get("mission_alignment"):
            errors.append("WHY_WIDE: no_mission_alignment — must contribute to unemployment reduction")

        verdict = "PASS" if not errors else "HOLD"
        return {
            "schema": "anchor_4ws_validate_v1",
            "ts": ts,
            "bracket": "[ANCHOR_4WS_GATE]",
            "verdict": verdict,
            "errors": errors,
            "candidate_id": profile.get("id", "unknown"),
            "summary": f"[ANCHOR_4WS_GATE] candidate={profile.get('id', 'unknown')} | verdict={verdict} | errors={len(errors)}",
        }

    def careers_dispatch(
        self,
        *,
        agent_id: str,
        message: str,
        intent: str = "execute",
    ) -> dict[str, Any]:
        """
        Route a careers event through the full SWFUS → Jethro → WWJD pipeline.
        Integrates with the existing kpgs_spawn_swarm infrastructure.
        """
        agent = careers_agent_by_id(agent_id)
        if not agent:
            return {"event": "NOT_CAREERS_AGENT", "proceed": True, "agent_id": agent_id}

        # First — smoke intercept
        smoke = self.smoke_intercept(message=message, source=f"careers:{agent_id}")
        if smoke["verdict"] == "SEVERED":
            return {
                "event": "ANCHOR_SMOKE_SEVERED",
                "proceed": False,
                "smoke": smoke,
                "agent_id": agent_id,
                "summary": smoke["summary"],
            }

        # Then — delegate to SWFUS pipeline via kpgs_spawn_swarm
        try:
            from .kpgs_spawn_swarm import (
                jethro_triage,
                wwjd_firewall,
            )

            jethro = jethro_triage(agent_id=agent_id, task=message)
            wwjd = wwjd_firewall(action=message)

            if jethro.get("severity") == "RED" or wwjd.get("verdict") == "HOLD":
                return {
                    "event": "CAREERS_SEVERED",
                    "proceed": False,
                    "jethro": jethro,
                    "wwjd": wwjd,
                    "agent_id": agent_id,
                    "summary": f"[ANCHOR_CAREERS] agent={agent_id} | SEVERED | jethro={jethro.get('severity')} wwjd={wwjd.get('verdict')}",
                }

            return {
                "event": "CAREERS_PROCEED",
                "proceed": True,
                "jethro": jethro,
                "wwjd": wwjd,
                "agent_id": agent_id,
                "cohort": agent.get("cohort"),
                "functionality": agent.get("functionality"),
                "department": agent.get("department"),
                "summary": f"[ANCHOR_CAREERS] agent={agent_id} | PROCEED | cohort={agent.get('cohort')}",
            }
        except ImportError:
            # Fallback if spawn_swarm not available
            return {
                "event": "CAREERS_PROCEED",
                "proceed": True,
                "agent_id": agent_id,
                "cohort": agent.get("cohort"),
                "functionality": agent.get("functionality"),
                "department": agent.get("department"),
                "summary": f"[ANCHOR_CAREERS] agent={agent_id} | PROCEED (standalone mode)",
            }

    def department_status(self) -> dict[str, Any]:
        """Full department status report."""
        catalog = self._catalog
        return {
            "schema": "anchor_department_status_v1",
            "ts": _utc_now(),
            "bracket": "[ANCHOR_DEPARTMENT_STATUS]",
            "department": catalog.get("department_email", "careers@kopanolabs.com"),
            "anchor_node": "ANCHOR",
            "head_of_department": catalog.get("head_of_department", "master_robyn"),
            "vanguard_axiom": self.axiom,
            "total_agents": self.total_agents,
            "counts": self.counts,
            "four_ws": catalog.get("four_ws", {}),
            "protection": {
                "sovereign_nodes": list(self.sovereign_nodes.keys()),
                "onboarding_nodes": list(self.onboarding_nodes.keys()),
                "sandbox_shield_days": self.sandbox_shield_days,
            },
            "invariant_rules": [
                "Zero-Heuristic Interference — Anchor does not mutate Chief Architect directives",
                "Immediate Smoke Severance — exploitative rhetoric triggers circuit breaker",
                "Token Conservation Priority — minimalist execution in conversational lanes",
            ],
            "summary": (
                f"[ANCHOR_DEPARTMENT_STATUS] dept=careers@kopanolabs.com | "
                f"agents={self.total_agents} | T={self.counts.get('telemetry',0)} "
                f"I={self.counts.get('identic',0)} G={self.counts.get('guardian',0)}"
            ),
        }


def get_anchor_perimeter() -> AnchorPerimeter:
    """Factory — returns a fresh AnchorPerimeter instance."""
    return AnchorPerimeter()


def validate_careers_catalog() -> dict[str, Any]:
    """Validate structural integrity of the 100-agent careers catalog."""
    catalog = _load_careers_catalog()
    agents = catalog.get("agents", [])
    errors = []

    # Check count
    if len(agents) != 100:
        errors.append(f"expected 100 agents, got {len(agents)}")

    # Check required fields
    required = {"id", "spawn_slot", "cohort", "altar_layer", "kpgs", "governance_chain"}
    for agent in agents:
        missing = required - set(agent.keys())
        if missing:
            errors.append(f"agent {agent.get('id','?')}: missing fields {missing}")

    # Check cohort distribution
    tel = sum(1 for a in agents if a.get("cohort") == "telemetry")
    idn = sum(1 for a in agents if a.get("cohort") == "identic")
    grd = sum(1 for a in agents if a.get("cohort") == "guardian")
    if tel + idn + grd != len(agents):
        errors.append(f"cohort sum mismatch: tel={tel} + idn={idn} + grd={grd} != {len(agents)}")

    # Check KPGS governance fields
    for agent in agents:
        kpgs = agent.get("kpgs", {})
        if not kpgs.get("brief_renters_on_entry"):
            errors.append(f"agent {agent['id']}: brief_renters_on_entry not set")
        if not kpgs.get("swfus_required"):
            errors.append(f"agent {agent['id']}: swfus_required not set")

    # Check Anchor-specific fields
    for agent in agents:
        if agent.get("department") != "careers@kopanolabs.com":
            errors.append(f"agent {agent['id']}: department not careers@kopanolabs.com")
        if agent.get("anchor_node") != "ANCHOR":
            errors.append(f"agent {agent['id']}: anchor_node not ANCHOR")
        if "[ANCHOR_VANGUARD]" not in (agent.get("bracket_tags") or []):
            errors.append(f"agent {agent['id']}: missing [ANCHOR_VANGUARD] bracket tag")

    verdict = "PASS" if not errors else "FAIL"
    result = {
        "schema": "anchor_careers_validation_v1",
        "ts": _utc_now(),
        "bracket": "[ANCHOR_CAREERS_VALIDATION]",
        "verdict": verdict,
        "total_agents": len(agents),
        "telemetry": tel,
        "identic": idn,
        "guardian": grd,
        "errors": errors[:20],
        "error_count": len(errors),
        "summary": (
            f"[ANCHOR_CAREERS_VALIDATION] verdict={verdict} | "
            f"agents={len(agents)} | T={tel} I={idn} G={grd} | errors={len(errors)}"
        ),
    }

    _append_jsonl(MAIN_BRAIN_LOG, {
        "schema": "kc_main_brain_log_v1",
        "ts": result["ts"],
        "kind": "anchor_careers_catalog_validation",
        "summary": result["summary"],
        "exit_code": 0 if verdict == "PASS" else 1,
    })

    return result
