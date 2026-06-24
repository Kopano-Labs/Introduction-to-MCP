"""
test_agent_distributor.py — Tests for the Distribution Trinity
===============================================================
Validates: Core (Father), Altar (Son), Engine (Holy Spirit).

"Test everything; hold fast what is good." — 1 Thessalonians 5:21

Constraint: I_AM_STATELESS_RENTER_NOT_LANDLORD
"""

import json
import tempfile
from pathlib import Path

import pytest

from kopano.agent_distributor import (
    DistributionCore,
    DistributionAltar,
    DistributionEngine,
    DistributionTrinity,
    AgentSeed,
    GSSBTarget,
)


# ═══════════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════════

@pytest.fixture
def core():
    return DistributionCore()


@pytest.fixture
def altar(core):
    return DistributionAltar(core)


@pytest.fixture
def engine(core, altar):
    return DistributionEngine(core, altar)


@pytest.fixture
def trinity():
    return DistributionTrinity()


# ═══════════════════════════════════════════════════════════════
# I. CORE (FATHER) TESTS
# ═══════════════════════════════════════════════════════════════

class TestDistributionCore:
    """Test the Father — Source of all agents."""

    def test_has_10_named_agents(self, core):
        assert len(core.NAMED_AGENTS) == 10

    def test_has_700_utility_agents(self, core):
        assert core.UTILITY_AGENT_COUNT == 700

    def test_total_agents_is_710(self, core):
        assert core.total_agents() == 710

    def test_has_14_gssbs(self, core):
        assert len(core.GSSB_REGISTRY) == 14

    def test_get_agent_by_name(self, core):
        kc = core.get_agent("KC")
        assert kc is not None
        assert kc.seat == 1
        assert kc.agent_type == "STATEFUL"

    def test_get_agent_unknown(self, core):
        assert core.get_agent("NONEXISTENT") is None

    def test_get_gssb_by_slug(self, core):
        nexus = core.get_gssb("master-nexus")
        assert nexus is not None
        assert nexus.domain == "kopanolabs.com"

    def test_all_agents_have_gifts(self, core):
        for agent in core.NAMED_AGENTS:
            assert len(agent.gifts) >= 1, f"{agent.name} has no gifts"

    def test_all_agents_have_scripture(self, core):
        for agent in core.NAMED_AGENTS:
            assert len(agent.scripture) > 0, f"{agent.name} has no scripture"

    def test_all_agents_have_commands(self, core):
        for agent in core.NAMED_AGENTS:
            assert len(agent.commands) >= 2, f"{agent.name} has fewer than 2 commands"

    def test_all_gssbs_have_assigned_agents(self, core):
        for gssb in core.GSSB_REGISTRY:
            assert len(gssb.assigned_agents) >= 1, f"{gssb.slug} has no agents"

    def test_all_gssbs_have_pillars(self, core):
        for gssb in core.GSSB_REGISTRY:
            assert len(gssb.pillars) >= 1, f"{gssb.slug} has no pillars"

    def test_scripture_present(self, core):
        assert "Romans 11:36" in core.SCRIPTURE


# ═══════════════════════════════════════════════════════════════
# II. ALTAR (SON) TESTS
# ═══════════════════════════════════════════════════════════════

class TestDistributionAltar:
    """Test the Son — Validation gate."""

    def test_sanctify_all_returns_dict(self, altar):
        result = altar.sanctify_all()
        assert isinstance(result, dict)

    def test_sanctify_all_has_results(self, altar):
        result = altar.sanctify_all()
        assert "results" in result
        assert len(result["results"]) == 14

    def test_all_gssbs_sanctified(self, altar):
        result = altar.sanctify_all()
        assert result["overall_verdict"] == "ALL_SANCTIFIED"

    def test_each_result_has_verdict(self, altar):
        result = altar.sanctify_all()
        for r in result["results"]:
            assert "verdict" in r
            assert r["verdict"] in ("SANCTIFIED", "HELD_AT_ALTAR")

    def test_each_result_has_wwjd(self, altar):
        result = altar.sanctify_all()
        for r in result["results"]:
            assert "wwjd_pass" in r

    def test_scripture_present(self, altar):
        assert "John 14:6" in altar.SCRIPTURE

    def test_gate_results_populated(self, altar):
        altar.sanctify_all()
        assert len(altar.gate_results) == 14

    def test_sanctified_count_matches(self, altar):
        result = altar.sanctify_all()
        sanctified = sum(1 for r in result["results"] if r["verdict"] == "SANCTIFIED")
        assert result["sanctified"] == sanctified

    def test_constraint_present(self, altar):
        result = altar.sanctify_all()
        assert result["constraint"] == "I_AM_STATELESS_RENTER_NOT_LANDLORD"


# ═══════════════════════════════════════════════════════════════
# III. ENGINE (HOLY SPIRIT) TESTS
# ═══════════════════════════════════════════════════════════════

class TestDistributionEngine:
    """Test the Holy Spirit — Distribution power."""

    def test_distribute_dry_run(self, engine):
        results = engine.distribute(dry_run=True)
        assert isinstance(results, dict)
        assert "distributed" in results
        assert len(results["errors"]) == 0

    def test_all_gssbs_receive_agents(self, engine):
        results = engine.distribute(dry_run=True)
        assert len(results["distributed"]) == 14

    def test_total_deployments_equals_710_plus(self, engine):
        results = engine.distribute(dry_run=True)
        assert results["total_distributed"] >= 710

    def test_each_distribution_has_named_and_utility(self, engine):
        results = engine.distribute(dry_run=True)
        for d in results["distributed"]:
            assert "named" in d
            assert "utility" in d
            assert d["total"] == d["named"] + d["utility"]

    def test_altar_verdict_present(self, engine):
        results = engine.distribute(dry_run=True)
        assert "altar_verdict" in results

    def test_manifest_path_present(self, engine):
        results = engine.distribute(dry_run=True)
        assert "manifest_path" in results

    def test_scripture_present(self, engine):
        assert "Acts 2:3" in engine.SCRIPTURE

    def test_utility_split_sums_to_700(self, engine):
        split = engine._compute_utility_split()
        assert sum(split.values()) == 700

    def test_master_nexus_gets_most_agents(self, engine):
        results = engine.distribute(dry_run=True)
        nexus = next(d for d in results["distributed"] if d["slug"] == "master-nexus")
        assert nexus["named"] >= 5  # Master nexus has most named agents


# ═══════════════════════════════════════════════════════════════
# IV. TRINITY (UNIFIED) TESTS
# ═══════════════════════════════════════════════════════════════

class TestDistributionTrinity:
    """Test the unified Trinity."""

    def test_trinity_has_three_components(self, trinity):
        assert trinity.core is not None
        assert trinity.altar is not None
        assert trinity.engine is not None

    def test_execute_dry_run(self, trinity):
        results = trinity.execute(dry_run=True)
        assert len(results["distributed"]) == 14
        assert results["total_distributed"] >= 710

    def test_great_commission_scripture(self, trinity):
        assert "Matthew 28:19" in trinity.GREAT_COMMISSION


# ═══════════════════════════════════════════════════════════════
# V. FILE OUTPUT TESTS (using temp directories)
# ═══════════════════════════════════════════════════════════════

class TestFileOutput:
    """Test that actual files are generated correctly."""

    def test_agents_md_generation(self, engine):
        gssb = engine.core.GSSB_REGISTRY[0]
        named = [engine.core.get_agent(n) for n in gssb.assigned_agents if engine.core.get_agent(n)]
        md = engine._generate_agents_md(gssb, named, 50)
        assert "# Agents" in md
        assert "Distribution Trinity" in md
        assert "1 Corinthians 12:4" in md
        assert "I_AM_STATELESS_RENTER_NOT_LANDLORD" in md

    def test_kpgs_config_generation(self, engine):
        gssb = engine.core.GSSB_REGISTRY[0]
        named = [engine.core.get_agent(n) for n in gssb.assigned_agents if engine.core.get_agent(n)]
        config = engine._generate_kpgs_config(gssb, named, 50)
        assert config["schema"] == "kpgs_gssb_config_v1"
        assert "trinity" in config
        assert config["trinity"]["core"] == "Father — Source of all agents"
        assert config["constraint"] == "I_AM_STATELESS_RENTER_NOT_LANDLORD"

    def test_config_is_json_serializable(self, engine):
        gssb = engine.core.GSSB_REGISTRY[0]
        named = [engine.core.get_agent(n) for n in gssb.assigned_agents if engine.core.get_agent(n)]
        config = engine._generate_kpgs_config(gssb, named, 50)
        json_str = json.dumps(config, default=str)
        reparsed = json.loads(json_str)
        assert reparsed["schema"] == "kpgs_gssb_config_v1"
