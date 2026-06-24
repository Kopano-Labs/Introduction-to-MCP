"""
test_gsmb_auto_runner.py — STAP 067-069: Auto Runner Tests
=============================================================
Tests for the GSMB Autonomous Governance Runner.

Constraint: I_AM_STATELESS_RENTER_NOT_LANDLORD
"""

import pytest
from kopano.gsmb_auto_runner import GSMBAutoRunner


class TestRunnerSingleTick:
    """STAP 067: Single tick execution."""

    def test_tick_returns_result(self):
        runner = GSMBAutoRunner()
        r = runner.tick()
        assert "tick_verdict" in r
        assert "nexus" in r
        assert "flows" in r
        assert "kc_ledger" in r
        assert "spawns" in r

    def test_tick_full_poc(self):
        runner = GSMBAutoRunner()
        r = runner.tick()
        assert r["tick_verdict"] in ("GSMB_FULL_POC", "GSMB_PARTIAL")

    def test_nexus_all_nso(self):
        runner = GSMBAutoRunner()
        r = runner.tick()
        assert r["nexus"]["nso_groups"] == 7

    def test_flows_adapted(self):
        runner = GSMBAutoRunner()
        r = runner.tick()
        assert r["flows"]["adapted"] == 5

    def test_kc_ledger_validated(self):
        runner = GSMBAutoRunner()
        r = runner.tick()
        assert r["kc_ledger"]["verdict"] == "KC_LEDGER_VALIDATED"
        assert r["kc_ledger"]["all_uphold"] is True

    def test_spawns_certified(self):
        runner = GSMBAutoRunner()
        r = runner.tick()
        assert r["spawns"]["total"] == 6
        assert r["spawns"]["certified"] == 6
        assert r["spawns"]["all_certified"] is True

    def test_has_constraint(self):
        runner = GSMBAutoRunner()
        r = runner.tick()
        assert r["constraint"] == "I_AM_STATELESS_RENTER_NOT_LANDLORD"

    def test_has_hebrews(self):
        runner = GSMBAutoRunner()
        r = runner.tick()
        assert r["hebrews_13_8"] is True

    def test_has_schema(self):
        runner = GSMBAutoRunner()
        r = runner.tick()
        assert r["schema"] == "gsmb_runner_tick_v1"


class TestRunnerMultipleTicks:
    """STAP 068: Multiple tick execution."""

    def test_two_ticks(self):
        runner = GSMBAutoRunner(interval_seconds=0)
        results = runner.run(cycles=2)
        assert len(results) == 2
        assert runner.tick_count == 2

    def test_tick_count_increments(self):
        runner = GSMBAutoRunner()
        runner.tick()
        runner.tick()
        assert runner.tick_count == 2

    def test_poc_accumulates(self):
        runner = GSMBAutoRunner(interval_seconds=0)
        results = runner.run(cycles=2)
        assert runner.total_poc + runner.total_foc == 2


class TestRunnerState:
    """STAP 069: Runner state management."""

    def test_initial_state(self):
        runner = GSMBAutoRunner()
        assert runner.tick_count == 0
        assert runner.total_poc == 0
        assert runner.total_foc == 0

    def test_custom_interval(self):
        runner = GSMBAutoRunner(interval_seconds=30)
        assert runner.interval == 30

    def test_auto_commit_default_off(self):
        runner = GSMBAutoRunner()
        assert runner.auto_commit is False
