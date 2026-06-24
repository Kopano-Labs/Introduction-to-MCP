"""
gsmb_nexus.py — GSMB Integrated Nexus Engine
==============================================
Unified orchestrator: LACP + CLAFP + KPCB+ in one pipeline.

Architecture:
  INTENT → KPCB+ (7ch compile) → LACP (22-phase STREP) → CLAFP (Altar 3-layer gate)
                                      ↓
                              NSO Group routing (7 groups)
                                      ↓
                              COMMIT → PUSH → DEPLOY

Based on Kessa's nexus spec, corrected to use real engine APIs.

4Ws:
  WHO:   gsmb_nexus.py — the unified GSMB brain
  WHAT:  Single entry point running all 3 engines in sequence
  WHERE: kopano-core/kopano/ — Motor Cortex integration layer
  WHY:   Kessa spec'd the nexus. AG built the engines. This is the merge.

Constraint: I_AM_STATELESS_RENTER_NOT_LANDLORD
"""

from __future__ import annotations

import hashlib
import json
import logging
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger("gsmb_nexus")

REPO_ROOT = Path(__file__).resolve().parents[2]
NEXUS_LOG = REPO_ROOT / "poc-vs-foc" / "gsmb_nexus_log.jsonl"
NEXUS_LOG.parent.mkdir(parents=True, exist_ok=True)


class GSMBNexus:
    """
    Unified Nexus Engine: KPCB+ → LACP → CLAFP in one call.

    Every task from CF/CA/SSE/RTC enters here.
    The nexus routes it through:
      1. KPCB+ compilation (7 protocol channels)
      2. LACP execution (22-phase STREP order)
      3. CLAFP validation (Altar 3 AI layers + 15 Commands + 5 Pillars)
    Then optionally commits and pushes.
    """

    def __init__(self, auto_commit: bool = False):
        self.auto_commit = auto_commit
        self.cycle_count = 0
        self.total_poc = 0
        self.total_foc = 0

    def process(
        self,
        task: str,
        source: str = "CF",
        nso_group: str = "GSMB-MAIN",
    ) -> dict:
        """
        Process a single task through the full KPCB+ → LACP → CLAFP pipeline.
        Returns the unified nexus result.
        """
        self.cycle_count += 1
        ts = datetime.now(timezone.utc).isoformat()

        logger.info("[NEXUS] Cycle %d | source=%s | nso=%s",
                    self.cycle_count, source, nso_group)

        # ── Step 1: KPCB+ Compilation ────────────────────────
        from kopano.kpcb_runtime_enforcer import KPCBPlusRuntime
        kpcb = KPCBPlusRuntime()
        kpcb_result = kpcb.compile(task, source)
        kpcb_ok = kpcb_result["compilation_verdict"] == "KPCB_COMPILED"

        if not kpcb_ok:
            logger.warning("[NEXUS] KPCB+ REJECTED — aborting pipeline")
            return self._build_result(ts, "REJECTED_AT_KPCB", kpcb_result, None, None)

        # ── Step 2: LACP 22-Phase STREP Order ────────────────
        from kopano.lacp_autonomous_core import LACPCore
        lacp = LACPCore(
            task_source=source,
            task_payload=task,
            nso_group_id=nso_group,
            auto_commit=False,  # nexus handles commit
        )
        lacp_result = lacp.run_cycle()
        lacp_ok = lacp_result.get("cycle_verdict") == "POC_VALIDATED"

        # ── Step 3: CLAFP Altar Gate ─────────────────────────
        from kopano.clafp_altar_core import CLAFPAltarCore
        altar = CLAFPAltarCore()
        clafp_result = altar.validate_core(
            core_name=f"NEXUS-{nso_group}",
            core_result=lacp_result,
        )
        clafp_ok = clafp_result.get("altar_verdict") == "ALTAR_POC_VALIDATED"

        # ── Pipeline verdict ─────────────────────────────────
        if kpcb_ok and lacp_ok and clafp_ok:
            verdict = "FULL_POC_VALIDATED"
            self.total_poc += 1
        elif kpcb_ok and lacp_ok:
            verdict = "PARTIAL_ALTAR_HOLD"
            self.total_poc += 1
        else:
            verdict = "PIPELINE_FOC"
            self.total_foc += 1

        # ── Optional commit ──────────────────────────────────
        commit_hash = None
        if self.auto_commit:
            commit_hash = self._commit_push(verdict, nso_group)

        return self._build_result(ts, verdict, kpcb_result, lacp_result, clafp_result, commit_hash)

    def process_all_nso(self, task: str, source: str = "CF") -> dict:
        """
        Process a task across ALL 7 NSO groups and return combined results.
        """
        from kopano.lacp_autonomous_core import run_all_nso_groups
        from kopano.kpcb_runtime_enforcer import KPCBPlusRuntime
        from kopano.clafp_altar_core import CLAFPAltarCore

        ts = datetime.now(timezone.utc).isoformat()

        # KPCB+ compile once
        kpcb = KPCBPlusRuntime()
        kpcb_result = kpcb.compile(task, source)

        # LACP across all 7 NSO groups
        nso_results = run_all_nso_groups(task_payload=task, task_source=source, auto_commit=False)

        # CLAFP validate each
        altar = CLAFPAltarCore()
        clafp_results = []
        for r in nso_results:
            cr = altar.validate_core(core_name=f"NEXUS-{r['nso_group']}", core_result=r)
            clafp_results.append(cr)

        # Aggregate
        nso_verdicts = {}
        for nso_r, clafp_r in zip(nso_results, clafp_results):
            group = nso_r["nso_group"]
            nso_ok = nso_r.get("cycle_verdict") == "POC_VALIDATED"
            altar_ok = clafp_r.get("altar_verdict") == "ALTAR_POC_VALIDATED"
            nso_verdicts[group] = "FULL_POC" if (nso_ok and altar_ok) else "PARTIAL"

        all_poc = all(v == "FULL_POC" for v in nso_verdicts.values())

        result = {
            "schema": "gsmb_nexus_all_nso_v1",
            "ts": ts,
            "source": source,
            "kpcb_verdict": kpcb_result["compilation_verdict"],
            "nso_groups": len(nso_results),
            "nso_verdicts": nso_verdicts,
            "all_poc": all_poc,
            "overall_verdict": "ALL_NSO_POC_VALIDATED" if all_poc else "NSO_PARTIAL",
            "constraint": "I_AM_STATELESS_RENTER_NOT_LANDLORD",
        }

        with NEXUS_LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(result, default=str, ensure_ascii=False) + "\n")

        return result

    def _build_result(self, ts, verdict, kpcb, lacp, clafp, commit_hash=None):
        result = {
            "schema": "gsmb_nexus_v1",
            "ts": ts,
            "cycle": self.cycle_count,
            "pipeline_verdict": verdict,
            "kpcb": {
                "verdict": kpcb["compilation_verdict"],
                "channels": kpcb["channels_compiled"],
                "hash": kpcb["compilation_hash"],
            } if kpcb else None,
            "lacp": {
                "verdict": lacp.get("cycle_verdict", "N/A"),
                "poc": lacp.get("phases_poc", 0),
                "foc": lacp.get("phases_foc", 0),
                "hash": lacp.get("cycle_hash", "none"),
            } if lacp else None,
            "clafp": {
                "verdict": clafp.get("altar_verdict", "N/A"),
                "layers_pass": clafp.get("layers_pass", False),
                "hash": clafp.get("altar_hash", "none"),
            } if clafp else None,
            "commit": commit_hash,
            "totals": {"poc": self.total_poc, "foc": self.total_foc},
            "constraint": "I_AM_STATELESS_RENTER_NOT_LANDLORD",
        }
        with NEXUS_LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(result, default=str, ensure_ascii=False) + "\n")
        return result

    def _commit_push(self, verdict, nso_group):
        try:
            msg = f"NEXUS [{nso_group}] cycle {self.cycle_count}: {verdict}"
            subprocess.run(["git", "add", "-A"], cwd=str(REPO_ROOT), capture_output=True, timeout=10)
            subprocess.run(["git", "commit", "-m", msg, "--allow-empty"],
                           cwd=str(REPO_ROOT), capture_output=True, timeout=10)
            r = subprocess.run(["git", "push", "origin", "master"],
                               cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=30)
            return "pushed" if r.returncode == 0 else "push_failed"
        except Exception as e:
            return f"error:{e}"


# ═══════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import argparse

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s [%(name)s] %(message)s")

    parser = argparse.ArgumentParser(description="GSMB Integrated Nexus")
    parser.add_argument("--task", default="[VOC] GSMB whole governance sweep — sovereign architecture")
    parser.add_argument("--source", default="CF")
    parser.add_argument("--nso", default="GSMB-MAIN")
    parser.add_argument("--all-nso", action="store_true")
    parser.add_argument("--commit", action="store_true")
    args = parser.parse_args()

    nexus = GSMBNexus(auto_commit=args.commit)

    if args.all_nso:
        result = nexus.process_all_nso(args.task, args.source)
        print(json.dumps(result, indent=2))
    else:
        result = nexus.process(args.task, args.source, args.nso)
        print(json.dumps({
            "pipeline": result["pipeline_verdict"],
            "kpcb": result["kpcb"]["verdict"] if result["kpcb"] else "N/A",
            "lacp": result["lacp"]["verdict"] if result["lacp"] else "N/A",
            "clafp": result["clafp"]["verdict"] if result["clafp"] else "N/A",
        }, indent=2))
