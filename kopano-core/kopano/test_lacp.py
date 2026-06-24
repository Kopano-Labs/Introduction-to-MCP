"""
test_lacp_autonomous_core.py — Tests for LACP Engine
=====================================================
Tests every phase in the STREP order state machine.
Tests single NSO core and all-NSO sweep.

Constraint: I_AM_STATELESS_RENTER_NOT_LANDLORD
"""

import pytest
from kopano.lacp_autonomous_core import (
    LACPCore, Phase, STREP_ORDER,
    PhaseResult, spawn_nso_core, run_all_nso_groups,
)


class TestPhaseResult:
    def test_creates_with_auto_ts_and_hash(self):
        r = PhaseResult(phase="TEST", verdict="POC")
        assert r.ts
        assert r.hash
        assert len(r.hash) == 12

    def test_to_dict(self):
        r = PhaseResult(phase="X", verdict="FOC", data={"a": 1})
        d = r.to_dict()
        assert d["phase"] == "X"
        assert d["verdict"] == "FOC"
        assert d["data"]["a"] == 1


class TestSTREPOrder:
    def test_has_22_phases(self):
        assert len(STREP_ORDER) == 22

    def test_starts_with_sync(self):
        assert STREP_ORDER[0] == Phase.SYNC

    def test_ends_with_commit_push(self):
        assert STREP_ORDER[-1] == Phase.COMMIT_PUSH

    def test_contains_bmnp(self):
        assert Phase.BMNP in STREP_ORDER

    def test_contains_enforce(self):
        assert Phase.ENFORCE in STREP_ORDER

    def test_contains_rtc(self):
        assert Phase.RTC in STREP_ORDER

    def test_contains_pkap_twice(self):
        pkap_phases = [p for p in STREP_ORDER if "PKAP" in p.value]
        assert len(pkap_phases) == 2

    def test_contains_cbp_twice(self):
        cbp_phases = [p for p in STREP_ORDER if "CBP" in p.value]
        assert len(cbp_phases) == 2

    def test_contains_360_twice(self):
        p360 = [p for p in STREP_ORDER if "360" in p.value]
        assert len(p360) == 2

    def test_contains_vector_matrix_twice(self):
        vm = [p for p in STREP_ORDER if "VECTOR" in p.value]
        assert len(vm) == 2


class TestLACPCore:
    def setup_method(self):
        self.core = LACPCore(
            task_source="CF",
            task_payload="[VOC] Test task for LACP validation",
            nso_group_id="TEST-NSO",
            auto_commit=False,
        )

    def test_cycle_increments(self):
        assert self.core.cycle == 0
        self.core.run_cycle()
        assert self.core.cycle == 1

    def test_run_cycle_returns_dict(self):
        result = self.core.run_cycle()
        assert isinstance(result, dict)

    def test_cycle_has_schema(self):
        result = self.core.run_cycle()
        assert result["schema"] == "lacp_cycle_v1"

    def test_cycle_has_nso_group(self):
        result = self.core.run_cycle()
        assert result["nso_group"] == "TEST-NSO"

    def test_cycle_has_constraint(self):
        result = self.core.run_cycle()
        assert result["constraint"] == "I_AM_STATELESS_RENTER_NOT_LANDLORD"

    def test_all_22_phases_executed(self):
        result = self.core.run_cycle()
        assert result["phases_total"] == 22

    def test_cycle_has_hash(self):
        result = self.core.run_cycle()
        assert len(result["cycle_hash"]) == 16

    def test_cycle_verdict_exists(self):
        result = self.core.run_cycle()
        assert result["cycle_verdict"] in ("POC_VALIDATED", "PARTIAL_POC", "FOC_DOMINANT")

    def test_poc_count_correct(self):
        result = self.core.run_cycle()
        poc = result["phases_poc"]
        foc = result["phases_foc"]
        assert poc + foc == 22

    def test_phases_list_length(self):
        result = self.core.run_cycle()
        assert len(result["phases"]) == 22


class TestIndividualPhases:
    def setup_method(self):
        self.core = LACPCore(
            task_source="RTC",
            task_payload="[VOC] Individual phase test — governance validation",
            nso_group_id="PHASE-TEST",
            auto_commit=False,
        )

    def test_sync_phase(self):
        r = self.core._exec_sync()
        assert r.phase == "SYNC"
        assert r.verdict == "POC"

    def test_task_intake_with_payload(self):
        r = self.core._exec_task_intake()
        assert r.verdict == "POC"
        assert r.data["source"] == "RTC"

    def test_task_intake_no_payload(self):
        empty = LACPCore(task_payload="", auto_commit=False)
        r = empty._exec_task_intake()
        assert r.verdict == "FOC"

    def test_bmnp_phase(self):
        r = self.core._exec_bmnp()
        assert r.phase == "BMNP"
        assert r.verdict in ("POC", "FOC")

    def test_cbp_pass_1(self):
        r = self.core._exec_cbp(1)
        assert r.phase == "CBP"
        assert r.verdict == "POC"

    def test_cbp_pass_2(self):
        # Need to run pass 1 first to create NSO
        self.core._exec_cbp(1)
        r = self.core._exec_cbp(2)
        assert r.phase == "CBP_2"

    def test_pp_sandbox(self):
        r = self.core._exec_pp_sandbox(1)
        assert r.phase == "PP_SANDBOX"
        assert "sandbox_id" in r.data

    def test_release(self):
        r = self.core._exec_release(1)
        assert r.phase == "RELEASE"
        assert r.verdict == "POC"

    def test_pkap(self):
        # Run some phases first so PKAP has signals to count
        self.core._exec_cbp(1)
        self.core.phase_results.append(PhaseResult(phase="TEST", verdict="POC"))
        r = self.core._exec_pkap(1)
        assert r.phase == "PKAP"
        assert "pkanp_ratio" in r.data

    def test_vector_matrix_green(self):
        for _ in range(5):
            self.core.phase_results.append(PhaseResult(phase="X", verdict="POC"))
        r = self.core._exec_vector_matrix(1)
        assert r.data["apu_status"] == "GREEN"

    def test_vector_matrix_red(self):
        for _ in range(5):
            self.core.phase_results.append(PhaseResult(phase="X", verdict="FOC"))
        r = self.core._exec_vector_matrix(1)
        assert r.data["apu_status"] == "RED"

    def test_trig(self):
        r = self.core._exec_trig(1)
        assert "coverage_degrees" in r.data

    def test_360_protocol(self):
        r = self.core._exec_360(1)
        assert "360" in r.phase

    def test_rtc_unanimous(self):
        for _ in range(3):
            self.core.phase_results.append(PhaseResult(phase="X", verdict="POC"))
        r = self.core._exec_rtc()
        assert r.data["unanimous"] is True

    def test_rtc_split(self):
        self.core.phase_results.append(PhaseResult(phase="X", verdict="POC"))
        self.core.phase_results.append(PhaseResult(phase="X", verdict="FOC"))
        r = self.core._exec_rtc()
        assert r.data["unanimous"] is False

    def test_ubmnp(self):
        self.core._exec_cbp(1)
        r = self.core._exec_ubmnp()
        assert r.phase == "UBMNP"
        assert r.data["action"] == "BMNP_UNLOCKED"

    def test_enforce(self):
        r = self.core._exec_enforce()
        assert r.phase == "ENFORCE_POC_PURGE_FOC"

    def test_bp(self):
        r = self.core._exec_bp()
        assert r.phase == "BP"

    def test_commit_push_skip(self):
        r = self.core._exec_commit_push()
        assert r.data["action"] == "skip"


class TestNSOGroups:
    def test_spawn_single_nso(self):
        result = spawn_nso_core(
            nso_group_id="TEST-SINGLE",
            task_source="SSE",
            task_payload="[VOC] Single NSO core test",
            auto_commit=False,
        )
        assert result["nso_group"] == "TEST-SINGLE"
        assert result["cycle_verdict"] in ("POC_VALIDATED", "PARTIAL_POC", "FOC_DOMINANT")

    def test_run_all_nso_returns_7(self):
        results = run_all_nso_groups(
            task_payload="[VOC] All NSO sweep test",
            auto_commit=False,
        )
        assert len(results) == 7

    def test_all_nso_groups_named(self):
        results = run_all_nso_groups(
            task_payload="[VOC] Names test",
            auto_commit=False,
        )
        names = [r["nso_group"] for r in results]
        assert "GSMB-MAIN" in names
        assert "GSSMB-FSMP" in names
        assert "GSPMB-CC" in names
        assert "GSPMB-KL" in names
        assert "GSPMB-SS" in names
        assert "GSPMB-FA" in names
        assert "GSPMB-FF" in names

    def test_all_nso_have_verdicts(self):
        results = run_all_nso_groups(
            task_payload="[VOC] Verdict test",
            auto_commit=False,
        )
        for r in results:
            assert "cycle_verdict" in r


class TestMultipleCycles:
    def test_two_cycles(self):
        core = LACPCore(
            task_source="CF",
            task_payload="[VOC] Multi-cycle test",
            nso_group_id="MULTI-TEST",
            auto_commit=False,
        )
        r1 = core.run_cycle()
        r2 = core.run_cycle()
        assert r1["cycle"] == 1
        assert r2["cycle"] == 2
        assert r1["cycle_hash"] != r2["cycle_hash"]

    def test_cycle_hashes_unique(self):
        core = LACPCore(
            task_payload="[VOC] Hash uniqueness test",
            auto_commit=False,
        )
        hashes = set()
        for _ in range(3):
            r = core.run_cycle()
            hashes.add(r["cycle_hash"])
        assert len(hashes) == 3
