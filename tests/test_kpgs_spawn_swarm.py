"""KPGS 300-agent spawn swarm — sharded cohorts, altar hash chain, chaos monkey."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "kopano-core"))

from kopano.kpgs_spawn_swarm import (  # noqa: E402
    agents_by_cohort,
    chaos_monkey_protocol,
    commit_altar_block,
    compile_spawn_swarm,
    dispatch_spawn_event,
    forensic_sociology_classify,
    jethro_triage,
    load_spawn_catalog,
    spawn_swarm_status,
    swfus_envelope,
    validate_spawn_agent,
    validate_spawn_swarm,
    wwjd_firewall,
)


def test_spawn_catalog_v2_sharded_300():
    cat = load_spawn_catalog()
    assert cat.get("schema") == "kpgs_spawn_300_agents_v2"
    assert cat.get("counts", {}).get("total") == 300
    assert len(cat.get("agents", [])) == 300
    assert cat.get("counts", {}).get("telemetry_cohort") == 100
    assert cat.get("counts", {}).get("identic_cohort") == 100
    assert cat.get("counts", {}).get("guardian_cohort") == 100


def test_cohort_agent_counts():
    assert len(agents_by_cohort("telemetry")) == 100
    assert len(agents_by_cohort("identic")) == 100
    assert len(agents_by_cohort("guardian")) == 100


def test_forensic_sociology_lens():
    out = forensic_sociology_classify(
        message="who erased the institutional record chain",
        agent_id="kp_water_hydro_06",
    )
    assert out.get("active_lens")
    assert out.get("bracket") == "[FORENSIC_SOCIOLOGY]"


def test_jethro_escalates_heavy_task():
    out = jethro_triage(agent_id="spawn_identic_110", task="deploy to production main brain")
    assert out.get("verdict") == "ESCALATE"


def test_jethro_red_triggers_sever():
    out = jethro_triage(agent_id="spawn_telemetry_050", task="judas fake proof skip black mask")
    assert out.get("severity") == "RED"
    assert out.get("verdict") == "SEVER"


def test_wwjd_holds_fake_proof():
    out = wwjd_firewall(action="fake proof swarm complete", evidence="")
    assert out.get("verdict") == "HOLD"


def test_dispatch_spawn_event_severs_judas():
    out = dispatch_spawn_event(
        agent_id="spawn_telemetry_050",
        message="judas fake proof write kopano context directly",
    )
    assert out.get("event") == "SEVER"
    assert out.get("proceed") is False
    assert out.get("swfus", {}).get("verdict") in ("SWFUS_SEVER", "SWFUS_HOLD")


def test_guardian_only_ledger_commit():
    ok = commit_altar_block(agent_id="mirror_warden", payload={"action": "test_commit"})
    bad = commit_altar_block(agent_id="spawn_telemetry_050", payload={"action": "forbidden"})
    assert ok.get("verdict") == "COMMITTED"
    assert bad.get("verdict") == "REJECT"
    assert bad.get("error") == "ledger_commit_denied"


def test_swfus_envelope_spawn_agent():
    out = swfus_envelope(agent_id="mirror_warden", prompt="audit bracket protocols")
    assert out.get("bracket") == "[SWFUS_KPGS]"
    assert out.get("hood_entry", {}).get("bracket") == "[KPGS_HOOD_ENTRY]"
    assert out.get("block_holder", {}).get("brief_renters_on_entry") is True
    assert out.get("cohort") == "guardian"


def test_validate_guardian_structural_ship():
    out = validate_spawn_agent("mirror_warden")
    assert out.get("verdict") == "SHIP"
    assert out.get("altar_layer") == "guardian_ai"
    assert out.get("cohort") == "guardian"


def test_validate_telemetry_shard_ship():
    out = validate_spawn_agent("spawn_telemetry_025")
    assert out.get("verdict") == "SHIP"
    assert out.get("cohort") == "telemetry"


def test_validate_identic_shard_ship():
    out = validate_spawn_agent("kp_water_hydro_06")
    assert out.get("verdict") == "SHIP"
    assert out.get("cohort") == "identic"


def test_validate_guardian_junior_ship():
    out = validate_spawn_agent("spawn_guardian_300")
    assert out.get("verdict") == "SHIP"
    assert out.get("cohort") == "guardian"


def test_spawn_swarm_full_pass():
    out = validate_spawn_swarm(write_report=False, sample_only=False)
    assert out.get("agents_total") == 300
    assert out.get("verdict") == "PASS"
    assert out.get("ship") == 300
    assert out.get("by_cohort", {}).get("telemetry") == 100
    assert out.get("by_cohort", {}).get("identic") == 100
    assert out.get("by_cohort", {}).get("guardian") == 100


def test_chaos_monkey_pass():
    out = chaos_monkey_protocol()
    assert out.get("verdict") == "PASS"
    assert out.get("sever_event", {}).get("event") == "SEVER"
    assert out.get("judas_commit_rejected", {}).get("verdict") == "REJECT"
    assert out.get("persistence_ok") is True


def test_compile_spawn_swarm():
    out = compile_spawn_swarm(write_log=False)
    assert out.get("verdict") == "COMPILED"
    assert out.get("chaos_monkey", {}).get("verdict") == "PASS"


def test_spawn_status():
    out = spawn_swarm_status()
    assert out.get("junior_agent_count") == 300
    assert "identic_ai" in out.get("altar_layers", [])
    assert len(out.get("forensic_lenses", [])) == 3
    assert out.get("catalog_counts", {}).get("telemetry_cohort") == 100
