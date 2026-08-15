"""Compatibility checks for the current GSMB runner class API."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "kopano-core"))

from kopano.gsmb_auto_runner import GSMBAutoRunner  # noqa: E402


@pytest.fixture(scope="module")
def tick_result() -> dict:
    """Share one real governance tick across the compatibility assertions."""
    return GSMBAutoRunner().tick()


def test_tick_produces_current_verdict(tick_result: dict) -> None:
    assert tick_result["tick_verdict"] in ("GSMB_FULL_POC", "GSMB_PARTIAL")


def test_tick_contains_current_sections(tick_result: dict) -> None:
    assert {"nexus", "flows", "kc_ledger", "spawns"} <= set(tick_result)


def test_tick_contains_constraint(tick_result: dict) -> None:
    assert tick_result["constraint"] == "I_AM_STATELESS_RENTER_NOT_LANDLORD"


def test_tick_uses_current_schema(tick_result: dict) -> None:
    assert tick_result["schema"] == "gsmb_runner_tick_v1"


def test_runner_counts_tick(tick_result: dict) -> None:
    assert tick_result["tick"] == 1
