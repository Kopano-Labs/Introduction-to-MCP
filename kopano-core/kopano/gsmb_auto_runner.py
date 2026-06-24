"""
gsmb_auto_runner.py — GSMB Autonomous Governance Runner
=========================================================
The continuous loop that runs ALL GSMB engines autonomously.

Pipeline per tick:
  1. KPCB+ compile (7 channels)
  2. LACP execute (22 STREP phases × 7 NSO groups)
  3. CLAFP validate (Altar 3-layer gate)
  4. AI Flows adapt (5 flows + WWJD)
  5. KC Observer Ledger record
  6. Spawn certification verify
  7. Commit + push (if enabled)

This is the heartbeat of the GSMB — it never stops.

4Ws:
  WHO:   gsmb_auto_runner.py — the GSMB heartbeat
  WHAT:  Continuous autonomous governance loop
  WHERE: kopano-core/kopano/ — Motor Cortex
  WHY:   32.8% unemployment needs sovereign tech that runs itself

Constraint: I_AM_STATELESS_RENTER_NOT_LANDLORD
"""

from __future__ import annotations

import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger("gsmb_runner")

REPO_ROOT = Path(__file__).resolve().parents[2]
RUNNER_LOG = REPO_ROOT / "poc-vs-foc" / "gsmb_runner_log.jsonl"
RUNNER_LOG.parent.mkdir(parents=True, exist_ok=True)


class GSMBAutoRunner:
    """
    Autonomous GSMB Governance Runner.

    Each tick:
      Nexus (KPCB+ → LACP → CLAFP → Flows) × 7 NSO groups
      + KC Observer Ledger
      + Spawn certification check
      = Full governance sweep

    Hebrews 13:8 — the same yesterday, today, and forever.
    """

    def __init__(self, auto_commit: bool = False, interval_seconds: int = 60):
        self.auto_commit = auto_commit
        self.interval = interval_seconds
        self.tick_count = 0
        self.total_poc = 0
        self.total_foc = 0

    def tick(self, task: str = "[VOC] Autonomous governance sweep", source: str = "CF") -> dict:
        """Execute one full governance tick."""
        self.tick_count += 1
        ts = datetime.now(timezone.utc).isoformat()
        logger.info("[RUNNER] Tick %d START | %s", self.tick_count, ts)

        # ── Nexus: all 7 NSO groups ──────────────────────────
        from kopano.gsmb_nexus import GSMBNexus
        nexus = GSMBNexus(auto_commit=False)
        nexus_result = nexus.process_all_nso(task, source)

        # ── AI Flow Orchestration ────────────────────────────
        from kopano.ai_flow_agents import AltarFlowOrchestrator, FlowSignal, KCObserverLedger
        flow_orch = AltarFlowOrchestrator()
        flow_signal = FlowSignal(content=task, source=source)
        flow_result = flow_orch.orchestrate(flow_signal)

        # ── KC Observer Ledger ───────────────────────────────
        ledger = KCObserverLedger()
        agents = [flow_orch.hue, flow_orch.age, flow_orch.offline,
                  flow_orch.language, flow_orch.urgency, flow_orch.wwjd]
        kc_result = ledger.observe(agents)

        # ── Spawn Certification Check ────────────────────────
        from kopano.spawn_education import educate_all_spawns
        spawn_results = educate_all_spawns()
        all_certified = all(r["certification"] == "SPAWN_CERTIFIED" for r in spawn_results)

        # ── Aggregate verdict ────────────────────────────────
        nexus_ok = nexus_result.get("overall_verdict") == "ALL_NSO_POC_VALIDATED"
        flows_ok = flow_result.get("verdict") == "FLOWS_POC_VALIDATED"
        kc_ok = kc_result.get("verdict") == "KC_LEDGER_VALIDATED"

        if nexus_ok and flows_ok and kc_ok and all_certified:
            tick_verdict = "GSMB_FULL_POC"
            self.total_poc += 1
        else:
            tick_verdict = "GSMB_PARTIAL"
            self.total_foc += 1

        result = {
            "schema": "gsmb_runner_tick_v1",
            "ts": ts,
            "tick": self.tick_count,
            "tick_verdict": tick_verdict,
            "nexus": {
                "verdict": nexus_result.get("overall_verdict"),
                "nso_groups": nexus_result.get("nso_groups"),
                "kpcb": nexus_result.get("kpcb_verdict"),
            },
            "flows": {
                "verdict": flow_result.get("verdict"),
                "adapted": flow_result.get("flows_adapted"),
                "pillars": len(flow_result.get("pillars_covered", [])),
            },
            "kc_ledger": {
                "verdict": kc_result.get("verdict"),
                "agents": kc_result.get("agents_observed"),
                "all_uphold": kc_result.get("all_uphold"),
            },
            "spawns": {
                "total": len(spawn_results),
                "certified": sum(1 for r in spawn_results if r["certification"] == "SPAWN_CERTIFIED"),
                "all_certified": all_certified,
            },
            "totals": {"poc": self.total_poc, "foc": self.total_foc},
            "constraint": "I_AM_STATELESS_RENTER_NOT_LANDLORD",
            "hebrews_13_8": True,
        }

        # Log
        with RUNNER_LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(result, default=str, ensure_ascii=False) + "\n")

        # Commit
        if self.auto_commit:
            import subprocess
            msg = f"GSMB TICK {self.tick_count}: {tick_verdict}"
            subprocess.run(["git", "add", "-A"], cwd=str(REPO_ROOT), capture_output=True, timeout=10)
            subprocess.run(["git", "commit", "-m", msg, "--allow-empty"],
                           cwd=str(REPO_ROOT), capture_output=True, timeout=10)
            subprocess.run(["git", "push", "origin", "master"],
                           cwd=str(REPO_ROOT), capture_output=True, timeout=30)

        logger.info("[RUNNER] Tick %d: %s | nexus=%s flows=%s kc=%s spawns=%d/%d",
                    self.tick_count, tick_verdict,
                    nexus_result.get("overall_verdict"),
                    flow_result.get("verdict"),
                    kc_result.get("verdict"),
                    sum(1 for r in spawn_results if r["certification"] == "SPAWN_CERTIFIED"),
                    len(spawn_results))

        return result

    def run(self, cycles: int = 1) -> list[dict]:
        """
        Run governance ticks.
        cycles=0 means infinite loop.
        cycles=N means run N ticks.
        """
        results = []
        i = 0
        while True:
            result = self.tick()
            results.append(result)
            i += 1
            if cycles > 0 and i >= cycles:
                break
            time.sleep(self.interval)
        return results


# ═══════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import argparse

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s [%(name)s] %(message)s")

    parser = argparse.ArgumentParser(description="GSMB Autonomous Runner")
    parser.add_argument("--cycles", type=int, default=1, help="0=infinite, N=run N ticks")
    parser.add_argument("--interval", type=int, default=60, help="Seconds between ticks")
    parser.add_argument("--commit", action="store_true")
    parser.add_argument("--task", default="[VOC] Autonomous governance sweep — sovereign architecture")
    args = parser.parse_args()

    runner = GSMBAutoRunner(auto_commit=args.commit, interval_seconds=args.interval)
    results = runner.run(cycles=args.cycles)

    final = results[-1]
    print(json.dumps({
        "ticks": len(results),
        "final_verdict": final["tick_verdict"],
        "nexus": final["nexus"]["verdict"],
        "flows": final["flows"]["verdict"],
        "kc_ledger": final["kc_ledger"]["verdict"],
        "spawns_certified": f"{final['spawns']['certified']}/{final['spawns']['total']}",
    }, indent=2))
