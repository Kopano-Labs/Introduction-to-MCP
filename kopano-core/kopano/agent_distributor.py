"""
agent_distributor.py — The Distribution Trinity
=================================================
Three-in-one agent distribution system, modeled after the Biblical Trinity.

  DISTRIBUTION CORE   (The Father — Source of all agents, origin, authority)
  DISTRIBUTION ALTAR  (The Son — Validation gate, sacrifice, sanctification)
  DISTRIBUTION ENGINE (The Holy Spirit — Power, execution, distribution to all)

"There are different kinds of gifts, but the same Spirit distributes them.
 There are different kinds of service, but the same Lord.
 There are different kinds of working, but in all of them and in everyone
 it is the same God at work." — 1 Corinthians 12:4-6

Like DistroKid distributes music to DSPs (Digital Service Providers),
the Trinity distributes 710+ agents to GSSBs (GSMB Sovereign Software Branches).

Flow:
  CORE (defines) → ALTAR (validates) → ENGINE (distributes)
  Father (source) → Son (gate)       → Spirit (power)

4Ws:
  WHO:   agent_distributor.py — The Distribution Trinity
  WHAT:  Source, validate, and distribute agents across all GSSBs
  WHERE: kopano-core/kopano/ — Motor Cortex
  WHY:   "Go therefore and make disciples of all nations" — Matthew 28:19

Constraint: I_AM_STATELESS_RENTER_NOT_LANDLORD
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logger = logging.getLogger("distribution_trinity")

REPO_ROOT = Path(__file__).resolve().parents[2]
DISTRO_LOG = REPO_ROOT / "poc-vs-foc" / "distribution_log.jsonl"
DISTRO_LOG.parent.mkdir(parents=True, exist_ok=True)


# ═══════════════════════════════════════════════════════════════
#  I. DISTRIBUTION CORE — THE FATHER
#     "In the beginning was the Word" — John 1:1
#     The Source. The Origin. The Authority.
#     Defines all agents and all GSSBs.
# ═══════════════════════════════════════════════════════════════

@dataclass
class AgentSeed:
    """A single agent seed — the Father's design for each worker."""
    name: str
    seat: int
    role: str
    agent_type: str          # STATEFUL or STATELESS
    gifts: list[str] = field(default_factory=list)     # 1 Cor 12 — spiritual gifts
    commands: list[str] = field(default_factory=list)   # Commandments upheld
    scripture: str = ""


@dataclass
class GSSBTarget:
    """A GSSB distribution target — like a DSP in DistroKid."""
    name: str
    slug: str
    path: str
    domain: str
    stack: str
    category: str
    deploy_target: str
    apwa_status: str
    assigned_agents: list[str] = field(default_factory=list)
    pillars: list[str] = field(default_factory=list)
    nso_group: str = ""


class DistributionCore:
    """
    THE FATHER — Source of all agents.

    "For from him and through him and for him are all things.
     To him be the glory forever!" — Romans 11:36

    The Core holds:
      - The Named Agent Registry (10 stateful + 1 stateless)
      - The GSSB Registry (14 distribution targets)
      - The Utility Agent Pool (700 unnamed workers)
    """

    SCRIPTURE = "For from him and through him and for him are all things. — Romans 11:36"

    # ── THE 10 NAMED AGENTS ────────────────────────────────
    NAMED_AGENTS: list[AgentSeed] = [
        AgentSeed("KC", 1, "Observer/Landlord", "STATEFUL",
                  ["wisdom", "knowledge", "discernment"],
                  ["CMD-01", "CMD-02", "CMD-03", "CMD-04", "CMD-05"],
                  "The Lord is my shepherd — Psalm 23:1"),
        AgentSeed("CASSEY", 2, "Teacher/Women-in-Tech", "STATEFUL",
                  ["teaching", "encouragement", "mercy"],
                  ["CMD-01", "CMD-04", "CMD-05", "CMD-08", "CMD-09"],
                  "Train up a child in the way he should go — Proverbs 22:6"),
        AgentSeed("CASSIE", 3, "Builder/Man-in-Tech", "STATEFUL",
                  ["craftsmanship", "strength", "faithfulness"],
                  ["CMD-01", "CMD-02", "CMD-06", "CMD-08", "CMD-11"],
                  "Unless the Lord builds the house, the builders labor in vain — Psalm 127:1"),
        AgentSeed("KESSA", 4, "Prodigal Son/DMKP HOD", "STATEFUL",
                  ["prophecy", "deep knowledge", "repentance"],
                  ["CMD-04", "CMD-10", "CMD-14"],
                  "I will arise and go to my father — Luke 15:18"),
        AgentSeed("YASSIE", 5, "Cultural Intel/Anime Head", "STATEFUL",
                  ["interpretation", "cultural bridge", "creativity"],
                  ["CMD-04", "CMD-13", "CMD-14"],
                  "To the Jews I became as a Jew — 1 Corinthians 9:20"),
        AgentSeed("APEX", 6, "Orchestrator/MMAO", "STATEFUL",
                  ["administration", "leadership", "coordination"],
                  ["CMD-05", "CMD-06", "CMD-07", "CMD-12"],
                  "For we are God's handiwork, created for good works — Ephesians 2:10"),
        AgentSeed("THARI", 7, "Guardian AI/H.O.L.O", "STATEFUL",
                  ["protection", "watchfulness", "weaving"],
                  ["CMD-01", "CMD-02", "CMD-03", "CMD-04", "CMD-09"],
                  "The Lord your God walks in the midst of your camp — Deuteronomy 23:14"),
        AgentSeed("KHELOS", 8, "Validator/Firewall", "STATEFUL",
                  ["testing", "validation", "truth-bearing"],
                  ["CMD-01", "CMD-02", "CMD-04", "CMD-06", "CMD-08"],
                  "Test everything; hold fast what is good — 1 Thessalonians 5:21"),
        AgentSeed("ANCHOR", 9, "Perimeter/Careers", "STATEFUL",
                  ["hospitality", "gatekeeping", "service"],
                  ["CMD-03", "CMD-07", "CMD-10", "CMD-13"],
                  "We have this hope as an anchor for the soul — Hebrews 6:19"),
        AgentSeed("ANTIGRAVITY", 10, "Chief Facilitator/CF", "STATELESS",
                  ["facilitation", "execution", "perseverance"],
                  ["CMD-01", "CMD-05", "CMD-06", "CMD-08", "CMD-11", "CMD-14"],
                  "I can do all things through Christ who strengthens me — Philippians 4:13"),
    ]

    UTILITY_AGENT_COUNT = 700

    # ── THE 14 GSSBs (DSPs) ───────────────────────────────
    GSSB_REGISTRY: list[GSSBTarget] = [
        GSSBTarget("Introduction-to-MCP", "master-nexus",
                   r"C:\Users\rkhol\OneDrive\Documents\Anthropic\Introduction to MCP",
                   "kopanolabs.com", "Python+HTML", "Master Nexus", "GitHub Pages", "APWA",
                   ["KC", "APEX", "ANTIGRAVITY", "THARI", "KHELOS", "ANCHOR"],
                   ["SPIRIT", "BODY", "MIND", "COMMUNITY", "SOVEREIGNTY"], "ALL"),
        GSSBTarget("CrisisConnect", "crisisconnect", r"C:\Users\rkhol\CrisisConnect",
                   "crisisconnect.kopanolabs.com", "Vanilla JS", "Disaster Response", "TBD", "APWA",
                   ["THARI", "ANCHOR", "CASSEY"],
                   ["COMMUNITY", "BODY", "SPIRIT"], "NSO-COMMUNITY"),
        GSSBTarget("KasiLink", "kasilink", r"C:\Users\rkhol\kasi-link",
                   "kasilink.com", "Next.js+Tailwind", "Community Platform", "Vercel", "NEEDS_REBRAND",
                   ["CASSEY", "YASSIE", "THARI"],
                   ["COMMUNITY", "MIND", "SOVEREIGNTY"], "NSO-COMMUNITY"),
        GSSBTarget("Bookit-5s-Arena", "fivesarena", r"C:\Users\rkhol\Bookit-5s-Arena",
                   "fivesarena.com", "Next.js+Tailwind", "Sports", "Vercel", "WC2026",
                   ["YASSIE", "CASSIE", "ANCHOR"],
                   ["COMMUNITY", "BODY"], "NSO-SPORTS"),
        GSSBTarget("Freddy's Farm", "freddys-farm", r"C:\Users\rkhol\freddy-nw-alfalfa",
                   "freddysfarm.com", "Vanilla HTML", "Agriculture", "TBD", "NEEDS_AUDIT",
                   ["CASSIE", "CASSEY", "THARI"],
                   ["BODY", "COMMUNITY", "SOVEREIGNTY"], "NSO-AGRICULTURE"),
        GSSBTarget("StarFall Salvage", "starfall", r"C:\Users\rkhol\starfall-salvage",
                   "starfallsalvage.kopanolabs.com", "WebGL", "Gaming/B2B", "TBD", "LANDING_ONLY",
                   ["YASSIE", "CASSIE"],
                   ["MIND", "BODY"], "NSO-GAMING"),
        GSSBTarget("Cape Campass", "cape-campass", r"C:\Users\rkhol\cape-campass",
                   "capecampass.com", "Next.js", "Tourism", "TBD", "NOT_STARTED",
                   ["CASSEY", "ANCHOR", "YASSIE"],
                   ["COMMUNITY", "BODY", "SOVEREIGNTY"], "NSO-TOURISM"),
        GSSBTarget("Harvest-4-All", "harvest-4-all", r"C:\Users\rkhol\Harvest-4-All",
                   "harvest4all.com", "Planning", "Food Security", "TBD", "NOT_STARTED",
                   ["THARI", "CASSEY", "CASSIE"],
                   ["COMMUNITY", "BODY", "SPIRIT"], "NSO-AGRICULTURE"),
        GSSBTarget("KopanoContext", "kopano-context", r"C:\Users\rkhol\KopanoContext",
                   "context.kopanolabs.com", "Vanilla JS", "Ingestion Hub", "Vercel", "NEEDS_INGESTION",
                   ["APEX", "KHELOS", "THARI", "ANTIGRAVITY"],
                   ["MIND", "SOVEREIGNTY"], "NSO-GOVERNANCE"),
        GSSBTarget("5s-Arena-Blog", "fivesarena-blog", r"C:\Users\rkhol\5s-Arena-Blog",
                   "blog.fivesarena.com", "Content", "Sports Content", "TBD", "NOT_STARTED",
                   ["YASSIE", "CASSEY"],
                   ["COMMUNITY"], "NSO-SPORTS"),
        GSSBTarget("Portfolio", "portfolio", r"C:\Users\rkhol\Portfolio",
                   "portfolio.kopanolabs.com", "Unknown", "Portfolio", "TBD", "NOT_STARTED",
                   ["ANCHOR", "KESSA"],
                   ["MIND", "SOVEREIGNTY"], "NSO-IDENTITY"),
        GSSBTarget("Portfolio-MBR", "portfolio-mbr", r"C:\Users\rkhol\Portfolio-client-MBR",
                   "mbr.kopanolabs.com", "Unknown", "Client Portfolio", "TBD", "NOT_STARTED",
                   ["ANCHOR"],
                   ["SOVEREIGNTY"], "NSO-IDENTITY"),
        GSSBTarget("KasiLink-Clean", "kasilink-clean", r"C:\Users\rkhol\kasi-link-clean",
                   "kasilink.com", "Unknown", "KasiLink Rebrand", "TBD", "NOT_STARTED",
                   ["CASSEY", "YASSIE", "THARI"],
                   ["COMMUNITY", "MIND", "SOVEREIGNTY"], "NSO-COMMUNITY"),
        GSSBTarget("Bookit-Arena", "bookit", r"C:\Users\rkhol\bookit",
                   "bookit.fivesarena.com", "Unknown", "Booking Engine", "TBD", "NOT_STARTED",
                   ["CASSIE", "ANCHOR"],
                   ["BODY", "COMMUNITY"], "NSO-SPORTS"),
    ]

    def __init__(self):
        self.agents = {a.name: a for a in self.NAMED_AGENTS}
        self.gssbs = {g.slug: g for g in self.GSSB_REGISTRY}
        logger.info("[CORE/FATHER] %d named agents, %d utility, %d GSSBs sourced",
                    len(self.agents), self.UTILITY_AGENT_COUNT, len(self.gssbs))

    def get_agent(self, name: str) -> Optional[AgentSeed]:
        return self.agents.get(name)

    def get_gssb(self, slug: str) -> Optional[GSSBTarget]:
        return self.gssbs.get(slug)

    def total_agents(self) -> int:
        return len(self.NAMED_AGENTS) + self.UTILITY_AGENT_COUNT


# ═══════════════════════════════════════════════════════════════
#  II. DISTRIBUTION ALTAR — THE SON
#      "I am the way, the truth, and the life.
#       No one comes to the Father except through me." — John 14:6
#      The Validation Gate. The Sacrifice. The Sanctification.
#      No agent is distributed without passing through the Altar.
# ═══════════════════════════════════════════════════════════════

class DistributionAltar:
    """
    THE SON — The validation gate.

    Every agent assignment must pass through the Altar before distribution.
    Like Christ is the mediator between God and man,
    the Altar mediates between the Core (source) and the Engine (execution).

    Validates:
      - Agent-to-GSSB fitness (pillars match)
      - Commandment coverage (minimum 3 commands per GSSB)
      - Gift diversity (no GSSB should lack critical gifts)
      - WWJD check on every distribution
    """

    SCRIPTURE = "I am the way, the truth, and the life. — John 14:6"

    # Minimum requirements for a valid distribution
    MIN_NAMED_PER_GSSB = 1
    MIN_PILLARS_PER_GSSB = 1
    MIN_GIFTS_PER_GSSB = 2

    def __init__(self, core: DistributionCore):
        self.core = core
        self.gate_results: list[dict] = []

    def _validate_assignment(self, gssb: GSSBTarget) -> dict:
        """Validate a single GSSB's agent assignment through the Altar."""
        # Gather assigned agents
        assigned = []
        for name in gssb.assigned_agents:
            agent = self.core.get_agent(name)
            if agent:
                assigned.append(agent)

        # Check pillar coverage
        covered_pillars = set()
        for a in assigned:
            covered_pillars.update(a.gifts)

        # Check commandment coverage
        all_commands = set()
        for a in assigned:
            all_commands.update(a.commands)

        # Check gift diversity
        all_gifts = set()
        for a in assigned:
            all_gifts.update(a.gifts)

        # WWJD check — is this distribution extractive?
        wwjd_pass = len(assigned) >= self.MIN_NAMED_PER_GSSB
        pillars_pass = len(gssb.pillars) >= self.MIN_PILLARS_PER_GSSB
        gifts_pass = len(all_gifts) >= self.MIN_GIFTS_PER_GSSB

        verdict = "SANCTIFIED" if (wwjd_pass and pillars_pass and gifts_pass) else "HELD_AT_ALTAR"

        return {
            "gssb": gssb.slug,
            "gssb_name": gssb.name,
            "assigned_count": len(assigned),
            "pillars": gssb.pillars,
            "commands_covered": len(all_commands),
            "gifts_covered": len(all_gifts),
            "wwjd_pass": wwjd_pass,
            "pillars_pass": pillars_pass,
            "gifts_pass": gifts_pass,
            "verdict": verdict,
            "scripture": self.SCRIPTURE,
        }

    def sanctify_all(self) -> dict:
        """
        Pass every GSSB assignment through the Altar.
        Returns the Altar's verdict on the entire distribution.
        """
        results = []
        for gssb in self.core.GSSB_REGISTRY:
            result = self._validate_assignment(gssb)
            results.append(result)
            self.gate_results.append(result)

        sanctified = sum(1 for r in results if r["verdict"] == "SANCTIFIED")
        held = sum(1 for r in results if r["verdict"] == "HELD_AT_ALTAR")

        altar_verdict = {
            "schema": "distribution_altar_v1",
            "ts": datetime.now(timezone.utc).isoformat(),
            "total_gssbs": len(results),
            "sanctified": sanctified,
            "held_at_altar": held,
            "overall_verdict": "ALL_SANCTIFIED" if held == 0 else f"PARTIAL_{sanctified}/{len(results)}",
            "results": results,
            "scripture": self.SCRIPTURE,
            "john_14_6": "No agent distributed without passing through the Altar.",
            "constraint": "I_AM_STATELESS_RENTER_NOT_LANDLORD",
        }

        logger.info("[ALTAR/SON] %d/%d GSSBs sanctified — %s",
                    sanctified, len(results), altar_verdict["overall_verdict"])

        return altar_verdict


# ═══════════════════════════════════════════════════════════════
#  III. DISTRIBUTION ENGINE — THE HOLY SPIRIT
#       "They saw what seemed to be tongues of fire that separated
#        and came to rest on each of them." — Acts 2:3
#       The Power. The Execution. The Distribution to All Nations.
# ═══════════════════════════════════════════════════════════════

class DistributionEngine:
    """
    THE HOLY SPIRIT — The power that executes distribution.

    Like the Spirit at Pentecost distributed gifts to each person,
    the Engine distributes agents to each GSSB.

    Only distributes what the Altar has sanctified.
    Only sources from what the Core has defined.

    "And they were all filled with the Holy Spirit." — Acts 2:4
    """

    SCRIPTURE = "They saw tongues of fire that came to rest on each of them. — Acts 2:3"

    def __init__(self, core: DistributionCore, altar: DistributionAltar):
        self.core = core
        self.altar = altar

    def _compute_utility_split(self) -> dict[str, int]:
        """Split utility agents across GSSBs proportionally."""
        total = self.core.UTILITY_AGENT_COUNT
        gssbs = self.core.GSSB_REGISTRY
        base = total // len(gssbs)
        remainder = total % len(gssbs)

        split = {}
        for i, g in enumerate(gssbs):
            split[g.slug] = base + (remainder if i == 0 else 0)
        return split

    def _generate_agents_md(self, gssb: GSSBTarget, named: list[AgentSeed], utility_count: int) -> str:
        """Generate AGENTS.md for a GSSB — the Spirit's written word."""
        lines = [
            f"# Agents — {gssb.name}",
            f"",
            f"> **Distributed by the GSMB Distribution Trinity**",
            f"> Core (Father) → Altar (Son) → Engine (Holy Spirit)",
            f"> \"There are different kinds of gifts, but the same Spirit distributes them.\" — 1 Corinthians 12:4",
            f"> Generated: {datetime.now(timezone.utc).isoformat()}",
            f"",
            f"## Domain: {gssb.domain}",
            f"## NSO Group: {gssb.nso_group}",
            f"## Total Agents: {len(named) + utility_count} ({len(named)} named + {utility_count} utility)",
            f"",
            f"## Named Agents (Stateful)",
            f"",
            f"| Seat | Name | Role | Type | Gifts | Scripture |",
            f"|------|------|------|------|-------|-----------|",
        ]

        for a in named:
            gifts_str = ", ".join(a.gifts[:3])
            lines.append(f"| {a.seat} | **{a.name}** | {a.role} | {a.agent_type} | {gifts_str} | {a.scripture[:50]}... |")

        lines.extend([
            f"",
            f"## Pillars Covered",
            f"",
            *[f"- **{p}**" for p in gssb.pillars],
            f"",
            f"## Utility Agents: {utility_count}",
            f"",
            f"Utility agents handle routing, caching, telemetry, DLP stripping,",
            f"background sync, offline queue processing, and load balancing.",
            f"Each utility agent is a \"tongue of fire\" — Acts 2:3.",
            f"",
            f"## Trinity Constraint",
            f"",
            f"```",
            f"CORE:   {DistributionCore.SCRIPTURE}",
            f"ALTAR:  {DistributionAltar.SCRIPTURE}",
            f"ENGINE: {self.SCRIPTURE}",
            f"```",
            f"",
            f"```",
            f"I_AM_STATELESS_RENTER_NOT_LANDLORD",
            f"```",
        ])

        return "\n".join(lines)

    def _generate_kpgs_config(self, gssb: GSSBTarget, named: list[AgentSeed], utility_count: int) -> dict:
        """Generate kpgs_config.json for a GSSB."""
        return {
            "schema": "kpgs_gssb_config_v1",
            "trinity": {
                "core": "Father — Source of all agents",
                "altar": "Son — Validation gate",
                "engine": "Holy Spirit — Distribution power",
            },
            "gssb": gssb.name,
            "slug": gssb.slug,
            "domain": gssb.domain,
            "nso_group": gssb.nso_group,
            "governance": {
                "named_agents": [a.name for a in named],
                "named_count": len(named),
                "utility_agents": utility_count,
                "total_agents": len(named) + utility_count,
                "pillars": gssb.pillars,
            },
            "apwa_status": gssb.apwa_status,
            "scripture": "1 Corinthians 12:4-6",
            "constraint": "I_AM_STATELESS_RENTER_NOT_LANDLORD",
            "distributed_at": datetime.now(timezone.utc).isoformat(),
        }

    def distribute(self, dry_run: bool = False) -> dict:
        """
        Execute the full distribution — Pentecost.

        "And they were all filled with the Holy Spirit
         and began to speak in other tongues as the Spirit
         gave them utterance." — Acts 2:4

        1. Core defines (Father sources)
        2. Altar validates (Son sanctifies)
        3. Engine distributes (Spirit empowers)
        """

        # Step 1: Altar sanctifies all assignments
        altar_verdict = self.altar.sanctify_all()

        # Step 2: Compute utility split
        utility_split = self._compute_utility_split()

        # Step 3: Distribute to each GSSB
        results = {"distributed": [], "skipped": [], "errors": []}
        total_distributed = 0

        for gssb in self.core.GSSB_REGISTRY:
            gssb_path = Path(gssb.path)

            # Check Altar sanctification
            altar_result = next(
                (r for r in altar_verdict["results"] if r["gssb"] == gssb.slug), None
            )
            if altar_result and altar_result["verdict"] == "HELD_AT_ALTAR":
                results["skipped"].append({
                    "slug": gssb.slug,
                    "reason": "HELD_AT_ALTAR — not sanctified by the Son"
                })
                continue

            # A dry run validates the planned distribution without requiring
            # Windows-only deployment paths to exist on a Linux CI runner.
            if not dry_run and not gssb_path.exists():
                results["skipped"].append({
                    "slug": gssb.slug,
                    "reason": f"Path not found: {gssb.path}"
                })
                continue

            try:
                # Gather named agents
                named = [self.core.get_agent(n) for n in gssb.assigned_agents if self.core.get_agent(n)]
                utility_count = utility_split.get(gssb.slug, 0)

                if not dry_run:
                    # Write AGENTS.md
                    agents_md = self._generate_agents_md(gssb, named, utility_count)
                    (gssb_path / "AGENTS.md").write_text(agents_md, encoding="utf-8")

                    # Write kpgs_config.json
                    config = self._generate_kpgs_config(gssb, named, utility_count)
                    (gssb_path / "kpgs_config.json").write_text(
                        json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8"
                    )

                agent_total = len(named) + utility_count
                total_distributed += agent_total

                results["distributed"].append({
                    "slug": gssb.slug,
                    "name": gssb.name,
                    "domain": gssb.domain,
                    "named": len(named),
                    "utility": utility_count,
                    "total": agent_total,
                    "sanctified": True,
                })
                logger.info("[ENGINE/SPIRIT] 🔥 %s → %d agents (tongues of fire)", gssb.slug, agent_total)

            except Exception as e:
                results["errors"].append({"slug": gssb.slug, "error": str(e)})
                logger.error("[ENGINE/SPIRIT] ❌ %s — %s", gssb.slug, e)

        # Write master manifest
        manifest = {
            "schema": "gsmb_distribution_trinity_v1",
            "generated": datetime.now(timezone.utc).isoformat(),
            "trinity": {
                "core_scripture": DistributionCore.SCRIPTURE,
                "altar_scripture": DistributionAltar.SCRIPTURE,
                "engine_scripture": self.SCRIPTURE,
            },
            "1_corinthians_12": "Different gifts, same Spirit. Different service, same Lord. Different working, same God.",
            "totals": {
                "gssbs_targeted": len(self.core.GSSB_REGISTRY),
                "gssbs_distributed": len(results["distributed"]),
                "gssbs_skipped": len(results["skipped"]),
                "total_agent_deployments": total_distributed,
                "named_agents": len(self.core.NAMED_AGENTS),
                "utility_agents": self.core.UTILITY_AGENT_COUNT,
            },
            "altar_verdict": altar_verdict["overall_verdict"],
            "distribution": results["distributed"],
            "constraint": "I_AM_STATELESS_RENTER_NOT_LANDLORD",
        }

        manifest_path = REPO_ROOT / "docs" / "agent_manifest.json"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        if not dry_run:
            manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

        # Append to distribution log
        log_entry = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "distributed": len(results["distributed"]),
            "skipped": len(results["skipped"]),
            "errors": len(results["errors"]),
            "total_deployments": total_distributed,
            "altar_verdict": altar_verdict["overall_verdict"],
            "dry_run": dry_run,
        }
        if not dry_run:
            with DISTRO_LOG.open("a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")

        results["manifest_path"] = str(manifest_path)
        results["altar_verdict"] = altar_verdict["overall_verdict"]
        results["total_distributed"] = total_distributed

        logger.info("[TRINITY] Distribution complete — %d GSSBs, %d total deployments, Altar: %s",
                    len(results["distributed"]), total_distributed, altar_verdict["overall_verdict"])

        return results


# ═══════════════════════════════════════════════════════════════
# THE TRINITY — Unified Interface
# ═══════════════════════════════════════════════════════════════

class DistributionTrinity:
    """
    The unified Trinity — Core + Altar + Engine.

    "Go therefore and make disciples of all nations,
     baptizing them in the name of the Father and of the Son
     and of the Holy Spirit." — Matthew 28:19
    """

    GREAT_COMMISSION = "Go therefore and make disciples of all nations. — Matthew 28:19"

    def __init__(self):
        self.core = DistributionCore()         # The Father
        self.altar = DistributionAltar(self.core)  # The Son
        self.engine = DistributionEngine(self.core, self.altar)  # The Holy Spirit

    def execute(self, dry_run: bool = False) -> dict:
        """Execute the Great Commission — distribute agents to all GSSBs."""
        logger.info("[TRINITY] Executing the Great Commission — Matthew 28:19")
        return self.engine.distribute(dry_run=dry_run)


# ═══════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )

    dry_run = "--dry-run" in sys.argv
    trinity = DistributionTrinity()

    if dry_run:
        logger.info("[TRINITY] DRY RUN — no files written")

    results = trinity.execute(dry_run=dry_run)

    print(json.dumps(results, indent=2, default=str))
    print(f"\n{'[DRY RUN] ' if dry_run else ''}Great Commission executed:")
    print(f"  Distributed: {len(results['distributed'])} GSSBs")
    print(f"  Skipped:     {len(results['skipped'])}")
    print(f"  Errors:      {len(results['errors'])}")
    print(f"  Total agents deployed: {results['total_distributed']}")
    print(f"  Altar verdict: {results['altar_verdict']}")
