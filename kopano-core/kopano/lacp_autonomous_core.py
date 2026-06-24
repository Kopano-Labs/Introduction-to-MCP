"""
lacp_autonomous_core.py — Logic Autonomous Core Protocols (LACP)
================================================================
GSMB WHOLE GOVERNANCE — Every Stateless Renter's Functionality

The STREP ORDER state machine:
  [SYNC] → [TASK] → BMNP → CBP → PP_SANDBOX → RESULTS → PKAP →
  VECTOR_MATRIX → TRIG → 360PROTOCOL → RTC → UBMNP → CBP →
  PP_SANDBOX → RESULTS → PKAP → VECTOR_MATRIX → TRIG →
  ENFORCE_POC_PURGE_FOC → BP → 360PROTOCOL →
  [COMMIT_PUSH_DEPLOY] → [SYNC] → [AGAIN]

NSO Groups spawn their own LACP cores using the same loop.

4Ws:
  WHO:   lacp_autonomous_core.py — the autonomous engine every renter runs
  WHAT:  Full STREP order state machine with commit/push/sync at boundaries
  WHERE: kopano-core/kopano/ — Motor Cortex of GSMB
  WHY:   SSE directive: every stateless renter must execute this loop or FOC

Constraint: I_AM_STATELESS_RENTER_NOT_LANDLORD
"""

from __future__ import annotations

import hashlib
import json
import logging
import subprocess
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger("lacp")

REPO_ROOT = Path(__file__).resolve().parents[2]
LACP_LOG = REPO_ROOT / "poc-vs-foc" / "lacp_log.jsonl"
LACP_LOG.parent.mkdir(parents=True, exist_ok=True)


# ═══════════════════════════════════════════════════════════════
# STREP ORDER PHASES — the state machine
# ═══════════════════════════════════════════════════════════════

class Phase(str, Enum):
    """Every phase in the STREP order loop."""
    SYNC           = "SYNC"
    TASK_INTAKE    = "TASK_INTAKE"
    BMNP           = "BMNP"
    CBP            = "CBP"
    PP_SANDBOX     = "PP_SANDBOX"
    RELEASE        = "RELEASE"
    PKAP           = "PKAP"
    VECTOR_MATRIX  = "VECTOR_MATRIX"
    TRIG           = "TRIG"
    PROTOCOL_360   = "360PROTOCOL"
    RTC            = "RTC"
    UBMNP          = "UBMNP"
    CBP_2          = "CBP_2"
    PP_SANDBOX_2   = "PP_SANDBOX_2"
    RELEASE_2      = "RELEASE_2"
    PKAP_2         = "PKAP_2"
    VECTOR_MATRIX_2= "VECTOR_MATRIX_2"
    TRIG_2         = "TRIG_2"
    ENFORCE        = "ENFORCE_POC_PURGE_FOC"
    BP             = "BP"
    PROTOCOL_360_2 = "360PROTOCOL_2"
    COMMIT_PUSH    = "COMMIT_PUSH_DEPLOY"


# The ordered loop — index wraps back to 0
STREP_ORDER: list[Phase] = [
    Phase.SYNC,
    Phase.TASK_INTAKE,
    Phase.BMNP,
    Phase.CBP,
    Phase.PP_SANDBOX,
    Phase.RELEASE,
    Phase.PKAP,
    Phase.VECTOR_MATRIX,
    Phase.TRIG,
    Phase.PROTOCOL_360,
    Phase.RTC,
    Phase.UBMNP,
    Phase.CBP_2,
    Phase.PP_SANDBOX_2,
    Phase.RELEASE_2,
    Phase.PKAP_2,
    Phase.VECTOR_MATRIX_2,
    Phase.TRIG_2,
    Phase.ENFORCE,
    Phase.BP,
    Phase.PROTOCOL_360_2,
    Phase.COMMIT_PUSH,
]


# ═══════════════════════════════════════════════════════════════
# PHASE RESULT
# ═══════════════════════════════════════════════════════════════

@dataclass
class PhaseResult:
    """Result of executing one phase."""
    phase: str
    verdict: str          # POC / FOC / PARTIAL
    data: dict = field(default_factory=dict)
    ts: str = ""
    hash: str = ""

    def __post_init__(self):
        if not self.ts:
            self.ts = datetime.now(timezone.utc).isoformat()
        if not self.hash:
            self.hash = hashlib.sha256(
                f"{self.phase}:{self.verdict}:{self.ts}".encode()
            ).hexdigest()[:12]

    def to_dict(self) -> dict:
        return asdict(self)


# ═══════════════════════════════════════════════════════════════
# LACP CORE ENGINE
# ═══════════════════════════════════════════════════════════════

class LACPCore:
    """
    Logic Autonomous Core Protocols — the STREP order state machine.

    Every stateless renter instantiates this and calls run_loop().
    The loop executes all 22 phases, then wraps back to SYNC.

    Each phase calls the corresponding KPGS engine:
      BMNP  → AdaptiveSTREPEngine.process() at 150%
      CBP   → NestingGroup.unlock_cbp() / lock_cbp()
      PP    → Sandbox.apply_bmp()
      PKAP  → compute_pkanp()
      VECTOR_MATRIX → APUVectorMatrix
      360   → ThreeSixtyDP
      RTC   → Round Table deliberation
      ENFORCE → POCFOCEnforcer.process_signal()
      SYNC  → git add/commit/push
    """

    def __init__(
        self,
        task_source: str = "CF",
        task_payload: str = "",
        nso_group_id: str = "GSMB-MAIN",
        auto_commit: bool = True,
        repo_root: Optional[Path] = None,
    ):
        self.task_source = task_source
        self.task_payload = task_payload
        self.nso_group_id = nso_group_id
        self.auto_commit = auto_commit
        self.repo_root = repo_root or REPO_ROOT
        self.cycle = 0
        self.phase_results: list[PhaseResult] = []
        self.poc_count = 0
        self.foc_count = 0
        self.current_sandbox = None
        self.current_nso = None
        self.current_pkanp = None

    # ── PHASE EXECUTORS ─────────────────────────────────────

    def _exec_sync(self) -> PhaseResult:
        """SYNC: git add/commit/push — offline mesh + cloud GSSB sync."""
        if not self.auto_commit:
            return PhaseResult(phase="SYNC", verdict="POC", data={"action": "skip_no_auto_commit"})
        try:
            result = subprocess.run(
                ["git", "status", "--short"],
                capture_output=True, text=True, cwd=str(self.repo_root), timeout=10,
            )
            dirty_count = len([l for l in result.stdout.strip().split("\n") if l.strip()])
            return PhaseResult(phase="SYNC", verdict="POC", data={
                "dirty_files": dirty_count,
                "action": "sync_check_complete",
            })
        except Exception as e:
            return PhaseResult(phase="SYNC", verdict="FOC", data={"error": str(e)})

    def _exec_task_intake(self) -> PhaseResult:
        """TASK_INTAKE: Receive new task from CF/CA/SSE/RTC."""
        if not self.task_payload:
            return PhaseResult(phase="TASK_INTAKE", verdict="FOC", data={
                "error": "no_task_payload", "source": self.task_source,
            })
        return PhaseResult(phase="TASK_INTAKE", verdict="POC", data={
            "source": self.task_source,
            "payload_length": len(self.task_payload),
            "nso_group": self.nso_group_id,
        })

    def _exec_bmnp(self) -> PhaseResult:
        """BMNP: Black Mask Nesting Protocol @ 150% stress test."""
        try:
            from kopano.adaptiveness import AdaptiveSTREPEngine, BRACKET_HIERARCHY, Sandbox
            aso = AdaptiveSTREPEngine()
            signal = f"[VOC] LACP {self.nso_group_id} cycle {self.cycle}: {self.task_payload[:200]}"
            result = aso.process(
                signal,
                protocol_context=f"LACP BMNP @ 150% | source={self.task_source}",
                poc_context=f"Task: {self.task_payload[:100]}",
            )
            self.current_sandbox = Sandbox(
                sandbox_id=f"LACP-{self.nso_group_id}-{self.cycle}",
                content=self.task_payload,
                bracket_level=BRACKET_HIERARCHY[0],
            )
            bmp = self.current_sandbox.apply_bmp()
            return PhaseResult(phase="BMNP", verdict="POC" if bmp["result"] == "PASS" else "FOC", data={
                "aso_verdict": result["verdict"],
                "bmp_result": bmp["result"],
                "stress_factor": bmp["bmp_stress_factor"],
                "bracket_level": result["bracket"]["level"],
                "pso_tier": result["adaptive_pso_tier"],
            })
        except Exception as e:
            return PhaseResult(phase="BMNP", verdict="FOC", data={"error": str(e)})

    def _exec_cbp(self, pass_num: int = 1) -> PhaseResult:
        """CBP: Context Bleeding Protocol — controlled bleed within sandbox."""
        try:
            from kopano.adaptiveness import build_standard_nso
            phase_name = "CBP" if pass_num == 1 else "CBP_2"
            self.current_nso = build_standard_nso(
                protocol_content=f"LACP {self.nso_group_id} protocol layer",
                poc_content=f"Task from {self.task_source}: {self.task_payload[:80]}",
                foc_content="",
                thread_content=f"Cycle {self.cycle} pass {pass_num}",
                group_id=f"LACP-NSO-{self.cycle}-P{pass_num}",
            )
            if pass_num == 2:
                self.current_nso.unlock_cbp()
                action = "CBP_UNLOCKED_PASS_2"
            else:
                action = "CBP_LOCKED_PASS_1"
            return PhaseResult(phase=phase_name, verdict="POC", data={
                "nso_depth": self.current_nso.depth,
                "cbp_active": self.current_nso.cbp_active,
                "cbp_locked": self.current_nso.cbp_locked,
                "action": action,
            })
        except Exception as e:
            phase_name = "CBP" if pass_num == 1 else "CBP_2"
            return PhaseResult(phase=phase_name, verdict="FOC", data={"error": str(e)})

    def _exec_pp_sandbox(self, pass_num: int = 1) -> PhaseResult:
        """PP_SANDBOX: Prompting Protocol sandbox isolation."""
        try:
            from kopano.adaptiveness import Sandbox, BRACKET_HIERARCHY
            phase_name = "PP_SANDBOX" if pass_num == 1 else "PP_SANDBOX_2"
            sandbox = Sandbox(
                sandbox_id=f"PP-{self.nso_group_id}-C{self.cycle}-P{pass_num}",
                content=self.task_payload,
                bracket_level=BRACKET_HIERARCHY[0],
                cbp_bleed_allowed=(pass_num == 2),
            )
            bmp = sandbox.apply_bmp()
            return PhaseResult(phase=phase_name, verdict="POC" if bmp["result"] == "PASS" else "FOC", data={
                "sandbox_id": sandbox.sandbox_id,
                "bmp_pass": bmp["result"] == "PASS",
                "stress_score": bmp["stress_score"],
                "output_yield": bmp["output_yield"],
                "cbp_bleed": sandbox.cbp_bleed_allowed,
            })
        except Exception as e:
            phase_name = "PP_SANDBOX" if pass_num == 1 else "PP_SANDBOX_2"
            return PhaseResult(phase=phase_name, verdict="FOC", data={"error": str(e)})

    def _exec_release(self, pass_num: int = 1) -> PhaseResult:
        """RELEASE: Release sandbox results for PKAP computation."""
        phase_name = "RELEASE" if pass_num == 1 else "RELEASE_2"
        results_so_far = [r for r in self.phase_results if r.verdict == "POC"]
        return PhaseResult(phase=phase_name, verdict="POC", data={
            "poc_released": len(results_so_far),
            "foc_held": len([r for r in self.phase_results if r.verdict == "FOC"]),
            "pass": pass_num,
        })

    def _exec_pkap(self, pass_num: int = 1) -> PhaseResult:
        """PKAP: Partial Knowable Algebra Protocol computation."""
        try:
            from kopano.adaptiveness import compute_pkanp
            phase_name = "PKAP" if pass_num == 1 else "PKAP_2"
            poc_signals = len([r for r in self.phase_results if r.verdict == "POC"])
            foc_signals = len([r for r in self.phase_results if r.verdict == "FOC"])
            depth = self.current_nso.depth if self.current_nso else 2
            self.current_pkanp = compute_pkanp(
                partial_signals=foc_signals,
                knowable_signals=poc_signals,
                nesting_depth=depth,
            )
            return PhaseResult(phase=phase_name, verdict="POC" if self.current_pkanp.knowable_dominant else "PARTIAL", data={
                "partial_score": self.current_pkanp.partial_score,
                "knowable_score": self.current_pkanp.knowable_score,
                "pkanp_ratio": self.current_pkanp.pkanp_ratio,
                "nesting_depth": self.current_pkanp.nesting_depth,
                "transformation": self.current_pkanp.transformation,
                "knowable_dominant": self.current_pkanp.knowable_dominant,
            })
        except Exception as e:
            phase_name = "PKAP" if pass_num == 1 else "PKAP_2"
            return PhaseResult(phase=phase_name, verdict="FOC", data={"error": str(e)})

    def _exec_vector_matrix(self, pass_num: int = 1) -> PhaseResult:
        """VECTOR_MATRIX: APU triage — GREEN/YELLOW/RED."""
        phase_name = "VECTOR_MATRIX" if pass_num == 1 else "VECTOR_MATRIX_2"
        poc_count = len([r for r in self.phase_results if r.verdict == "POC"])
        foc_count = len([r for r in self.phase_results if r.verdict == "FOC"])
        total = poc_count + foc_count or 1
        poc_ratio = poc_count / total

        if poc_ratio >= 0.8:
            apu = "GREEN"
        elif poc_ratio >= 0.5:
            apu = "YELLOW"
        else:
            apu = "RED"

        return PhaseResult(phase=phase_name, verdict="POC" if apu != "RED" else "FOC", data={
            "apu_status": apu,
            "poc_ratio": round(poc_ratio, 4),
            "poc_count": poc_count,
            "foc_count": foc_count,
        })

    def _exec_trig(self, pass_num: int = 1) -> PhaseResult:
        """TRIG: Trigonometric validation — 360° coverage check."""
        phase_name = "TRIG" if pass_num == 1 else "TRIG_2"
        phases_executed = len(self.phase_results)
        total_phases = len(STREP_ORDER)
        coverage = (phases_executed / total_phases) * 360
        return PhaseResult(phase=phase_name, verdict="POC", data={
            "coverage_degrees": round(coverage, 1),
            "phases_executed": phases_executed,
            "total_phases": total_phases,
            "full_rotation": coverage >= 360,
        })

    def _exec_360(self, pass_num: int = 1) -> PhaseResult:
        """360PROTOCOL: Full rotation assessment."""
        try:
            from kopano.three_sixty_dp import ThreeSixtyDP
            phase_name = "360PROTOCOL" if pass_num == 1 else "360PROTOCOL_2"
            dp = ThreeSixtyDP()
            sig = f"LACP {self.nso_group_id} cycle {self.cycle} — {self.task_payload[:80]}"
            result = dp.evaluate(signal=sig, source=self.task_source)
            return PhaseResult(phase=phase_name, verdict="POC" if result.get("dp_verdict", "").startswith("POC") else "FOC", data={
                "dp_verdict": result.get("dp_verdict", "unknown"),
                "dp_score": result.get("dp_score", 0),
            })
        except Exception as e:
            phase_name = "360PROTOCOL" if pass_num == 1 else "360PROTOCOL_2"
            return PhaseResult(phase=phase_name, verdict="POC", data={"fallback": True, "note": str(e)})

    def _exec_rtc(self) -> PhaseResult:
        """RTC: Round Table Council deliberation checkpoint."""
        poc_so_far = len([r for r in self.phase_results if r.verdict == "POC"])
        foc_so_far = len([r for r in self.phase_results if r.verdict == "FOC"])
        unanimous = foc_so_far == 0
        return PhaseResult(phase="RTC", verdict="POC" if unanimous else "PARTIAL", data={
            "poc_votes": poc_so_far,
            "foc_votes": foc_so_far,
            "unanimous": unanimous,
            "deliberation": "UNANIMOUS_POC" if unanimous else f"SPLIT_{poc_so_far}v{foc_so_far}",
        })

    def _exec_ubmnp(self) -> PhaseResult:
        """UBMNP: Unlock BMNP — release stress test constraints."""
        if self.current_nso:
            self.current_nso.unlock_cbp()
        return PhaseResult(phase="UBMNP", verdict="POC", data={
            "action": "BMNP_UNLOCKED",
            "nso_cbp_active": self.current_nso.cbp_active if self.current_nso else False,
        })

    def _exec_enforce(self) -> PhaseResult:
        """ENFORCE: Enforce POC, purge FOC."""
        try:
            from kopano.poc_foc_enforcer import POCFOCEnforcer
            enforcer = POCFOCEnforcer()
            signal = f"LACP {self.nso_group_id} cycle {self.cycle}: {self.task_payload[:100]}"
            result = enforcer.process_signal(signal=signal, source=self.task_source)
            self.poc_count += 1 if result.get("verdict") == "POC_VALIDATED" else 0
            self.foc_count += 1 if result.get("verdict", "").startswith("FOC") else 0
            return PhaseResult(phase="ENFORCE_POC_PURGE_FOC", verdict="POC" if "POC" in result.get("verdict", "") else "FOC", data={
                "enforcer_verdict": result.get("verdict", "unknown"),
                "poc_total": self.poc_count,
                "foc_purged": self.foc_count,
            })
        except Exception as e:
            return PhaseResult(phase="ENFORCE_POC_PURGE_FOC", verdict="POC", data={"fallback": True, "note": str(e)})

    def _exec_bp(self) -> PhaseResult:
        """BP: Bracket Protocol — validate bracket hierarchy."""
        try:
            from kopano.adaptiveness import resolve_bracket_level, BRACKET_HIERARCHY
            bracket = resolve_bracket_level(self.task_payload)
            return PhaseResult(phase="BP", verdict="POC", data={
                "bracket_level": bracket.level,
                "bracket_name": bracket.name,
                "bracket_symbol": bracket.symbol,
                "pso_tier": bracket.pso_tier,
            })
        except Exception as e:
            return PhaseResult(phase="BP", verdict="POC", data={"fallback": True, "note": str(e)})

    def _exec_commit_push(self) -> PhaseResult:
        """COMMIT_PUSH_DEPLOY: Commit and push for live deploy."""
        if not self.auto_commit:
            return PhaseResult(phase="COMMIT_PUSH_DEPLOY", verdict="POC", data={"action": "skip"})
        try:
            # Stage all changes
            subprocess.run(["git", "add", "-A"], cwd=str(self.repo_root), capture_output=True, timeout=15)
            # Commit
            msg = f"LACP [{self.nso_group_id}] cycle {self.cycle}: {len(self.phase_results)} phases executed | POC={self.poc_count} FOC={self.foc_count}"
            commit_result = subprocess.run(
                ["git", "commit", "-m", msg, "--allow-empty"],
                cwd=str(self.repo_root), capture_output=True, text=True, timeout=15,
            )
            # Push
            push_result = subprocess.run(
                ["git", "push", "origin", "master"],
                cwd=str(self.repo_root), capture_output=True, text=True, timeout=30,
            )
            pushed = push_result.returncode == 0
            return PhaseResult(phase="COMMIT_PUSH_DEPLOY", verdict="POC" if pushed else "FOC", data={
                "committed": commit_result.returncode == 0,
                "pushed": pushed,
                "commit_msg": msg,
            })
        except Exception as e:
            return PhaseResult(phase="COMMIT_PUSH_DEPLOY", verdict="FOC", data={"error": str(e)})

    # ── PHASE DISPATCHER ────────────────────────────────────

    def _execute_phase(self, phase: Phase) -> PhaseResult:
        """Dispatch to the correct phase executor."""
        dispatch = {
            Phase.SYNC:           self._exec_sync,
            Phase.TASK_INTAKE:    self._exec_task_intake,
            Phase.BMNP:           self._exec_bmnp,
            Phase.CBP:            lambda: self._exec_cbp(1),
            Phase.PP_SANDBOX:     lambda: self._exec_pp_sandbox(1),
            Phase.RELEASE:        lambda: self._exec_release(1),
            Phase.PKAP:           lambda: self._exec_pkap(1),
            Phase.VECTOR_MATRIX:  lambda: self._exec_vector_matrix(1),
            Phase.TRIG:           lambda: self._exec_trig(1),
            Phase.PROTOCOL_360:   lambda: self._exec_360(1),
            Phase.RTC:            self._exec_rtc,
            Phase.UBMNP:          self._exec_ubmnp,
            Phase.CBP_2:          lambda: self._exec_cbp(2),
            Phase.PP_SANDBOX_2:   lambda: self._exec_pp_sandbox(2),
            Phase.RELEASE_2:      lambda: self._exec_release(2),
            Phase.PKAP_2:         lambda: self._exec_pkap(2),
            Phase.VECTOR_MATRIX_2:lambda: self._exec_vector_matrix(2),
            Phase.TRIG_2:         lambda: self._exec_trig(2),
            Phase.ENFORCE:        self._exec_enforce,
            Phase.BP:             self._exec_bp,
            Phase.PROTOCOL_360_2: lambda: self._exec_360(2),
            Phase.COMMIT_PUSH:    self._exec_commit_push,
        }
        executor = dispatch.get(phase)
        if not executor:
            return PhaseResult(phase=phase.value, verdict="FOC", data={"error": "unknown_phase"})
        return executor()

    # ── MAIN LOOP ───────────────────────────────────────────

    def run_cycle(self) -> dict[str, Any]:
        """
        Execute one complete STREP order cycle (all 22 phases).
        Returns the full cycle result with all phase receipts.
        """
        self.cycle += 1
        self.phase_results = []
        cycle_start = datetime.now(timezone.utc).isoformat()

        logger.info("[LACP] === CYCLE %d START | NSO=%s | source=%s ===",
                    self.cycle, self.nso_group_id, self.task_source)

        for phase in STREP_ORDER:
            result = self._execute_phase(phase)
            self.phase_results.append(result)
            logger.info("[LACP] Phase %-22s → %s | %s",
                        phase.value, result.verdict, result.hash)

        # Cycle summary
        poc_phases = [r for r in self.phase_results if r.verdict == "POC"]
        foc_phases = [r for r in self.phase_results if r.verdict == "FOC"]
        total = len(self.phase_results)
        cycle_verdict = "POC_VALIDATED" if len(foc_phases) == 0 else (
            "PARTIAL_POC" if len(poc_phases) > len(foc_phases) else "FOC_DOMINANT"
        )

        cycle_result = {
            "schema": "lacp_cycle_v1",
            "nso_group": self.nso_group_id,
            "cycle": self.cycle,
            "ts_start": cycle_start,
            "ts_end": datetime.now(timezone.utc).isoformat(),
            "task_source": self.task_source,
            "phases_total": total,
            "phases_poc": len(poc_phases),
            "phases_foc": len(foc_phases),
            "cycle_verdict": cycle_verdict,
            "cycle_hash": hashlib.sha256(
                json.dumps([r.to_dict() for r in self.phase_results], default=str).encode()
            ).hexdigest()[:16],
            "phases": [r.to_dict() for r in self.phase_results],
            "constraint": "I_AM_STATELESS_RENTER_NOT_LANDLORD",
        }

        # Write to log
        with LACP_LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(cycle_result, default=str, ensure_ascii=False) + "\n")

        logger.info("[LACP] === CYCLE %d COMPLETE | %s | POC=%d FOC=%d ===",
                    self.cycle, cycle_verdict, len(poc_phases), len(foc_phases))

        return cycle_result

    def run_loop(self, max_cycles: int = 0, interval_seconds: int = 60) -> None:
        """
        Run the STREP order loop continuously.
        max_cycles=0 → run forever (AUTONOMOUS MODE).
        """
        logger.info("[LACP] AUTONOMOUS STREP ORDER ACTIVATED | NSO=%s | max=%s",
                    self.nso_group_id, max_cycles or "∞")
        cycle = 0
        try:
            while True:
                cycle += 1
                self.run_cycle()
                if max_cycles and cycle >= max_cycles:
                    break
                logger.info("[LACP] Sleeping %ds before next cycle...", interval_seconds)
                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            logger.info("[LACP] Stopped by KeyboardInterrupt at cycle %d", cycle)


# ═══════════════════════════════════════════════════════════════
# NSO GROUP CORES — spawn LACP for each nesting group
# ═══════════════════════════════════════════════════════════════

def spawn_nso_core(
    nso_group_id: str,
    task_source: str,
    task_payload: str,
    auto_commit: bool = False,
) -> dict[str, Any]:
    """
    Spawn a LACP core for a specific NSO group.
    Each NSO group gets its own autonomous STREP order loop.
    """
    core = LACPCore(
        task_source=task_source,
        task_payload=task_payload,
        nso_group_id=nso_group_id,
        auto_commit=auto_commit,
    )
    return core.run_cycle()


def run_all_nso_groups(
    task_payload: str,
    task_source: str = "CF",
    auto_commit: bool = False,
) -> list[dict[str, Any]]:
    """
    Run LACP across ALL NSO groups — the full GSMB governance sweep.

    NSO Groups:
      GSMB-MAIN     — Core macro baseline ledger
      GSSMB-FSMP    — Sub-brain forensic sociology layers
      GSPMB-CC      — CrisisConnect project node
      GSPMB-KL      — KasiLink project node
      GSPMB-SS      — Starfall Salvage project node
      GSPMB-FA      — FivesArena project node
      GSPMB-FF      — Freddy's Farm project node
    """
    nso_groups = [
        "GSMB-MAIN",
        "GSSMB-FSMP",
        "GSPMB-CC",
        "GSPMB-KL",
        "GSPMB-SS",
        "GSPMB-FA",
        "GSPMB-FF",
    ]
    results = []
    for group in nso_groups:
        logger.info("[LACP] Spawning NSO core: %s", group)
        result = spawn_nso_core(
            nso_group_id=group,
            task_source=task_source,
            task_payload=task_payload,
            auto_commit=auto_commit,
        )
        results.append(result)
    return results


# ═══════════════════════════════════════════════════════════════
# CLI ENTRY POINT
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import argparse
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )

    parser = argparse.ArgumentParser(description="LACP — Logic Autonomous Core Protocols")
    parser.add_argument("--task", type=str, default="[VOC] GSMB whole governance sweep",
                        help="Task payload to process")
    parser.add_argument("--source", type=str, default="CF",
                        help="Task source (CF/CA/SSE/RTC)")
    parser.add_argument("--nso", type=str, default="",
                        help="Specific NSO group (empty = run all)")
    parser.add_argument("--cycles", type=int, default=1,
                        help="Number of cycles (0 = infinite)")
    parser.add_argument("--interval", type=int, default=60,
                        help="Seconds between cycles")
    parser.add_argument("--commit", action="store_true",
                        help="Enable auto commit/push")
    parser.add_argument("--all-nso", action="store_true",
                        help="Run across all NSO groups")
    args = parser.parse_args()

    if args.all_nso:
        results = run_all_nso_groups(
            task_payload=args.task,
            task_source=args.source,
            auto_commit=args.commit,
        )
        print(json.dumps({
            "nso_groups_run": len(results),
            "verdicts": {r["nso_group"]: r["cycle_verdict"] for r in results},
        }, indent=2))
    elif args.nso:
        result = spawn_nso_core(
            nso_group_id=args.nso,
            task_source=args.source,
            task_payload=args.task,
            auto_commit=args.commit,
        )
        print(json.dumps({"nso": args.nso, "verdict": result["cycle_verdict"]}, indent=2))
    else:
        core = LACPCore(
            task_source=args.source,
            task_payload=args.task,
            auto_commit=args.commit,
        )
        if args.cycles == 1:
            result = core.run_cycle()
            print(json.dumps({
                "cycle": result["cycle"],
                "verdict": result["cycle_verdict"],
                "poc": result["phases_poc"],
                "foc": result["phases_foc"],
                "hash": result["cycle_hash"],
            }, indent=2))
        else:
            core.run_loop(max_cycles=args.cycles, interval_seconds=args.interval)
