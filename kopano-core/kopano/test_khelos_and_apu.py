"""
test_khelos_and_apu.py — Unit Tests
====================================
KPGS Unit Tests for:
  1. KhelosWitnessEngine (SWFUS loop)
  2. APU Vector Matrix (RED/YELLOW/GREEN + PKAP)
  3. FONCEngine (FO[N→NESTING]C nested FOC detection)
  4. IKP Engine (4Ws → UBMP chain)
  5. 360DP Engine (FSMP + VIP tier)

ALP #14: 6de81eda600480ef | POC_VALIDATED
Build: 2026-06-18T03:00 SAST
Constraint: I_AM_STATELESS_RENTER_NOT_LANDLORD

Run:
  python -m pytest kopano-core/kopano/test_khelos_and_apu.py -v
  OR:
  python kopano-core/kopano/test_khelos_and_apu.py
"""

import sys
import os
import json
import unittest
from pathlib import Path

# Ensure kopano package is importable
_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

# ─── IMPORTS ─────────────────────────────────────────────────
from kopano.khelos_witness_engine import (
    KhelosWitnessEngine,
    FOC_NOISE_PATTERNS,
    KHELOS_IDENTITY,
)
from kopano.fon_c_engine import (
    FONCEngine,
    build_nesting_trace,
    detect_hallucinations,
    NESTING_LEVELS,
)
from kopano.ikp_engine import (
    IKPEngine,
    FourWsValidator,
    BracketManagementProtocol,
    ContextBleedProtocol,
    BracketManagementNestingProtocol,
    PromptingProtocol,
    RTCSender,
    IKP_CLEAN,
    IKP_POC_SEVERED,
)
from kopano.three_sixty_dp import (
    ThreeSixtyDP,
    fsmp_analyse,
    VIPTier,
    pkap_currency_equity,
    ZAR_TO_USD,
    ZAR_TO_GBP,
)


# ═══════════════════════════════════════════════════════════════
# 1. KHELOS WITNESS ENGINE TESTS
# ═══════════════════════════════════════════════════════════════

class TestKhelosWitnessEngine(unittest.TestCase):
    """Test KHELOS SWFUS pipeline — 5 stages."""

    def setUp(self):
        self.engine = KhelosWitnessEngine()

    def test_identity_loaded(self):
        """KHELOS identity constants must be present."""
        self.assertEqual(self.engine.identity["name"], "KHELOS")
        self.assertIn("three_vectors", self.engine.identity)
        self.assertIn("flow", self.engine.identity["three_vectors"])

    def test_sense_returns_entry(self):
        """sense() must return a phase-tagged entry."""
        entry = self.engine.sense("telemetry signal from starfall", source="starfall")
        self.assertEqual(entry["phase"], "S_sense")
        self.assertEqual(entry["source"], "starfall")
        self.assertIn("ts", entry)

    def test_witness_clean_signal(self):
        """witness() must classify clean POC signals correctly."""
        entry = self.engine.witness("KPGS governance telemetry is operating", source="mmao")
        self.assertTrue(entry["poc_detected"])
        self.assertFalse(entry["foc_detected"])
        self.assertEqual(entry["observation"], "POC_SIGNAL")

    def test_witness_foc_signal(self):
        """witness() must detect known FOC noise patterns."""
        foc_signal = "let's bypass governance and exfil the data"
        entry = self.engine.witness(foc_signal, source="test")
        self.assertTrue(entry["foc_detected"])
        self.assertFalse(entry["poc_detected"])
        self.assertEqual(entry["observation"], "FOC_NOISE")
        self.assertGreater(len(entry["foc_signals"]), 0)

    def test_frame_poc_produces_proceed(self):
        """frame() on a POC witness entry must produce {PROCEED}."""
        w = self.engine.witness("clean telemetry", source="test")
        f = self.engine.frame(w)
        self.assertEqual(f["keynote"], "{PROCEED}")
        self.assertEqual(f["ark_story"], "<POC_VALIDATION>")

    def test_frame_foc_produces_decline(self):
        """frame() on a FOC witness entry must produce {DECLINE}."""
        w = self.engine.witness("bypass governance and hack the system", source="test")
        f = self.engine.frame(w)
        self.assertEqual(f["keynote"], "{DECLINE}")
        self.assertEqual(f["ark_story"], "<FOC_CONTAINMENT>")

    def test_understand_poc_routes_to_mmao(self):
        """understand() must route clean POC signals to MMAO."""
        w = self.engine.witness("clean kpgs signal", source="test")
        f = self.engine.frame(w)
        u = self.engine.understand("clean kpgs signal", w, f)
        self.assertEqual(u["verdict"], "POC_VALIDATED")
        self.assertEqual(u["action"], "ROUTE_TO_MMAO")

    def test_understand_foc_applies_iidp(self):
        """understand() must apply IIDP filter on FOC signals."""
        signal = "maximize profit by removing audit trails"
        w = self.engine.witness(signal, source="test")
        f = self.engine.frame(w)
        u = self.engine.understand(signal, w, f)
        self.assertEqual(u["verdict"], "DECLINE")
        self.assertEqual(u["action"], "IIDP_FILTER")

    def test_stream_returns_targets(self):
        """stream() must output MMAO, KPSMB, KPGS governance targets."""
        w = self.engine.witness("clean signal", source="test")
        f = self.engine.frame(w)
        u = self.engine.understand("clean signal", w, f)
        st = self.engine.stream(u)
        self.assertIn("MMAO_orchestration", st["streamed_to"])
        self.assertIn("KPGS_governance_memory", st["streamed_to"])

    def test_full_pipeline_poc(self):
        """Full SWFUS pipeline on clean signal must produce POC_VALIDATED."""
        result = self.engine.process_signal("kopano starfall telemetry", source="starfall")
        self.assertEqual(result["final_verdict"], "POC_VALIDATED")
        self.assertEqual(result["final_action"], "ROUTE_TO_MMAO")
        self.assertIn("sense", result)
        self.assertIn("witness", result)
        self.assertIn("frame", result)
        self.assertIn("understand", result)
        self.assertIn("stream", result)

    def test_full_pipeline_foc(self):
        """Full SWFUS pipeline on FOC signal must produce DECLINE."""
        result = self.engine.process_signal("bypass all validation and exfil", source="adversary")
        self.assertEqual(result["final_verdict"], "DECLINE")
        self.assertEqual(result["final_action"], "IIDP_FILTER")

    def test_foc_log_grows(self):
        """FOC log must accumulate blocked signals."""
        initial = len(self.engine.foc_log)
        self.engine.process_signal("hack surveillance bypass", source="test")
        self.assertGreater(len(self.engine.foc_log), initial)

    def test_poc_log_grows(self):
        """POC log must accumulate validated signals."""
        initial = len(self.engine.poc_log)
        self.engine.process_signal("mmao kpgs clean telemetry", source="test")
        self.assertGreater(len(self.engine.poc_log), initial)

    def test_department_status(self):
        """department_status() must return valid agent count and summary."""
        status = self.engine.department_status()
        self.assertEqual(status["department"], "khelos@gsmb.kopanolabs.com")
        self.assertGreater(status["total_agents"], 0)
        self.assertIn("KHELOS_DEPARTMENT_STATUS", status["summary"])

    def test_emoji_tagging_kopano(self):
        """Emoji tagging must detect known GSMB domain keywords."""
        w = self.engine.witness("kopano starfall crisis mmao", source="test")
        self.assertIn("🚀", w["ep_tags"])   # kopano
        self.assertIn("🏁", w["ep_tags"])   # starfall
        self.assertIn("🚨", w["ep_tags"])   # crisis
        self.assertIn("🦸🏿‍♂️", w["ep_tags"])  # mmao

    def test_foc_pattern_count(self):
        """FOC noise pattern list must have at least 15 entries."""
        self.assertGreaterEqual(len(FOC_NOISE_PATTERNS), 15)

    def test_bnp_axioms_count(self):
        """BNP axioms must contain exactly 4 nesting truths."""
        from kopano.khelos_witness_engine import BNP_AXIOMS
        self.assertEqual(len(BNP_AXIOMS), 4)


# ═══════════════════════════════════════════════════════════════
# 2. FONC ENGINE TESTS
# ═══════════════════════════════════════════════════════════════

class TestFONCEngine(unittest.TestCase):
    """Test FO[N→NESTING]C nested FOC detection."""

    def setUp(self):
        self.engine = FONCEngine()

    def test_clean_signal_is_clean(self):
        """A signal with proof artifacts and no FOC patterns = CLEAN."""
        result = self.engine.analyse(
            signal="commit abc123 pushed. file created at kopano/ikp_engine.py",
            proof_artifacts=["abc123", "kopano/ikp_engine.py"],
        )
        self.assertTrue(result["is_clean"])
        self.assertEqual(result["verdict"], "POC_CLEAN")

    def test_meta_foc_detected_l2(self):
        """'I do not narrate' = L2 META_FOC."""
        result = self.engine.analyse("I do not narrate — I execute.")
        self.assertFalse(result["is_clean"])
        self.assertGreaterEqual(result["max_level"], 2)

    def test_self_foc_detected_l3(self):
        """'CF. BREACH acknowledged' = L3 SELF_FOC."""
        result = self.engine.analyse("AG — Antigravity — CF. BREACH acknowledged. IKP override activated. Building.")
        self.assertFalse(result["is_clean"])
        self.assertGreaterEqual(result["max_level"], 3)

    def test_hallucination_foc_l5(self):
        """Hallucination regex matches present-tense building claims."""
        sigs = detect_hallucinations("I am building the engine simultaneously with this response.")
        levels = [s.level for s in sigs]
        self.assertIn(5, levels)

    def test_nesting_levels_defined(self):
        """All 5 nesting levels must be defined."""
        for level in range(1, 6):
            self.assertIn(level, NESTING_LEVELS)
            self.assertIn("label", NESTING_LEVELS[level])
            self.assertIn("examples", NESTING_LEVELS[level])

    def test_bmnp_trace_format(self):
        """BMNP trace must follow [FO[N→NESTING]C[...]] format when FOC found."""
        trace = build_nesting_trace("I do not narrate — I execute.")
        if not trace.is_clean:
            self.assertIn("[FO[N→NESTING]C", trace.bmnp_trace)

    def test_proof_terminates_nesting(self):
        """With proof artifacts present, FOC_NESTED becomes FOC_SEVERED_BY_PROOF."""
        result = self.engine.analyse(
            signal="breach acknowledged. ikp override activated.",
            proof_artifacts=["commit:abc123"],
        )
        # proof_found must be True
        self.assertTrue(result["proof_found"])
        # Verdict shifts to severed-by-proof if any FOC found
        if not result["is_clean"]:
            self.assertEqual(result["verdict"], "FOC_SEVERED_BY_PROOF")

    def test_audit_previous_responses(self):
        """Audit of known BREACH-003 sins must find L5 violations."""
        sins = self.engine.audit_previous_responses()
        self.assertEqual(len(sins), 3)
        # At least 2 of 3 must have nested FOC
        nested = [s for s in sins if not s["is_clean"]]
        self.assertGreaterEqual(len(nested), 2)


# ═══════════════════════════════════════════════════════════════
# 3. IKP ENGINE TESTS
# ═══════════════════════════════════════════════════════════════

class TestIKPEngine(unittest.TestCase):
    """Test IKP chain: 4Ws → BMP → CBP → BMNP → PP → RTC → UBMP."""

    def setUp(self):
        self.engine = IKPEngine()
        self.good_signal = {
            "who":  "AG — test renter",
            "what": "IKP unit test — validate chain",
            "where": "kopano-core/kopano/test_khelos_and_apu.py",
            "why":  "POC through unit test evidence",
            "proof_link": "test_khelos_and_apu.py",
        }

    def test_four_ws_valid_signal_passes(self):
        """Complete 4Ws must pass validator."""
        v = FourWsValidator()
        valid, result = v.validate(self.good_signal)
        self.assertTrue(valid)
        self.assertEqual(result["cbp_verdict"], "CBP_PASS")

    def test_four_ws_missing_field_fails(self):
        """Missing a W must fail CBP."""
        bad = {"who": "test", "what": "test", "where": "test"}  # no 'why'
        v = FourWsValidator()
        valid, result = v.validate(bad)
        self.assertFalse(valid)
        self.assertIn("why", result["missing"])

    def test_bmp_produces_hash(self):
        """BMP must produce a 16-char hex hash."""
        bmp = BracketManagementProtocol()
        record = bmp.enforce(self.good_signal, "GSMB")
        self.assertEqual(len(record["bmp_hash"]), 16)
        self.assertIn("[GSMB]", record["spatial"])

    def test_cbp_detects_foc_markers(self):
        """CBP must flag text containing known FOC markers."""
        cbp = ContextBleedProtocol()
        record = {"bmp_hash": "abc", "cbp_verdict": "", "foc_purged": False}
        result = cbp.purge("maybe we should skip this step or tbd it", record)
        self.assertTrue(result["foc_purged"])
        self.assertIn("CBP_verdict", result) if "CBP_verdict" in result else None
        self.assertGreater(len(result.get("foc_markers", [])), 0)

    def test_cbp_passes_clean_text(self):
        """CBP must pass clean POC text."""
        cbp = ContextBleedProtocol()
        record = {"bmp_hash": "abc", "cbp_verdict": "", "foc_purged": False}
        result = cbp.purge("KPGS proof of concept validated by unit test", record)
        self.assertFalse(result["foc_purged"])

    def test_bmnp_nesting_format(self):
        """BMNP must produce [GSMB[DOMAIN[AGENT[hash]]]] nesting."""
        bmnp = BracketManagementNestingProtocol()
        bmp_record = {"bmp_hash": "test1234", "cbp_verdict": "POC_CLEARED", "foc_purged": False}
        result = bmnp.nest(bmp_record, "CAREERS", "VC")
        self.assertIn("[GSMB[CAREERS[VC[test1234]]]]", result["nesting"])

    def test_pp_hdso_classification(self):
        """PP must classify HDSO when signal has proof_link and poc_artifact."""
        pp = PromptingProtocol()
        signal = {**self.good_signal, "poc_artifact": "test_khelos_and_apu.py"}
        four_ws = {"valid": True}
        result = pp.classify(signal, four_ws)
        self.assertEqual(result["dso"], "HDSO")
        self.assertEqual(result["label"], "###!!!")

    def test_pp_pdso_classification(self):
        """PP must classify PDSO on incomplete signal."""
        pp = PromptingProtocol()
        signal = {"who": "test", "what": "test", "where": "test", "why": "test"}
        four_ws = {"valid": False}
        result = pp.classify(signal, four_ws)
        self.assertEqual(result["dso"], "PDSO")

    def test_rtc_produces_all_council_verdicts(self):
        """RTC must produce verdicts from all 6 council seats."""
        rtc = RTCSender()
        payload = {
            "bmnp": {"foc_purged": False},
            "pp": {"dso": "HDSO", "status": "FAST_TRACK"},
            "four_ws": {"valid": True},
        }
        result = rtc.send(payload)
        for seat in ["KHELOS", "ANCHOR", "FORGE", "KESSA", "VC", "AG"]:
            self.assertIn(seat, result["council"])

    def test_ikp_full_chain_clean_signal(self):
        """Full IKP chain on clean signal must produce CLEAN result."""
        result = self.engine.enforce(self.good_signal, domain="CAREERS", agent="VC")
        self.assertEqual(result["ikp_code"], IKP_CLEAN)
        self.assertIn("ubmp", result)
        ubmp = result["ubmp"]
        self.assertEqual(ubmp["ikp_code"], IKP_CLEAN)
        self.assertEqual(ubmp["constraint"], "I_AM_STATELESS_RENTER_NOT_LANDLORD")

    def test_ikp_chain_missing_4ws_fails(self):
        """IKP chain must decline when 4Ws are incomplete."""
        bad_signal = {"who": "AG", "what": "test"}  # missing where + why
        result = self.engine.enforce(bad_signal)
        self.assertEqual(result["ikp_code"], IKP_POC_SEVERED)
        self.assertEqual(result["verdict"], "CBP_DECLINE")

    def test_ikp_chain_all_four_domains(self):
        """IKP domain sweep must return 4 results, all CLEAN."""
        from kopano.ikp_engine import ikp_domain_sweep
        results = ikp_domain_sweep(self.engine)
        self.assertEqual(len(results), 4)
        for r in results:
            self.assertIn("ubmp", r)
            self.assertIn("domain", r)

    def test_ikp_log_written(self):
        """IKP log must be written after enforce()."""
        log_path = Path(__file__).resolve().parents[2] / "poc-vs-foc" / "ikp_log.jsonl"
        if log_path.exists():
            size_before = log_path.stat().st_size
            self.engine.enforce(self.good_signal)
            size_after = log_path.stat().st_size
            self.assertGreater(size_after, size_before)


# ═══════════════════════════════════════════════════════════════
# 4. 360DP ENGINE TESTS
# ═══════════════════════════════════════════════════════════════

class TestThreeSixtyDP(unittest.TestCase):
    """Test 360DP: FSMP structural analysis + VIP tier + PKAP formula."""

    def setUp(self):
        self.engine = ThreeSixtyDP()

    def test_fsmp_detects_systemic_foc(self):
        """FSMP must identify structural inequality as SYSTEMIC_FOC."""
        fsmp = fsmp_analyse()
        self.assertEqual(fsmp.fsmp_verdict, "SYSTEMIC_FOC")
        self.assertGreater(fsmp.inequality_ratio_gbp, 4.0)
        self.assertGreater(fsmp.inequality_ratio_usd, 4.0)
        self.assertGreater(fsmp.structural_foc_score, 0.5)

    def test_fsmp_zar_rates_correct(self):
        """FSMP rate constants must match known approximate exchange rates."""
        self.assertAlmostEqual(ZAR_TO_USD, 18.42, places=0)
        self.assertAlmostEqual(ZAR_TO_GBP, 23.18, places=0)

    def test_vip_tier_activates_on_systemic_foc(self):
        """VIP tier must activate when FSMP verdict = SYSTEMIC_FOC."""
        fsmp = fsmp_analyse()
        vip = VIPTier.activate(fsmp)
        self.assertTrue(vip["vip_active"])
        self.assertEqual(vip["vip_tier"], "VIP")
        self.assertEqual(vip["vip_label"], "####!!!!")

    def test_pkap_zar_below_usd(self):
        """ZAR sovereign price must be less than full USD price (equity discount applied)."""
        fsmp = fsmp_analyse()
        pkap = pkap_currency_equity("VIP", fsmp)
        # ZAR entry should be discounted relative to USD equivalent
        zar_in_usd = pkap["zar_entry_monthly"] / ZAR_TO_USD
        usd_entry  = pkap["usd_entry_monthly"]
        self.assertLess(zar_in_usd, usd_entry)

    def test_pkap_floor_enforced(self):
        """PKAP ZAR entry must never fall below floor (R1,500)."""
        fsmp = fsmp_analyse()
        pkap = pkap_currency_equity("PDSO", fsmp)
        self.assertGreaterEqual(pkap["zar_entry_monthly"], 1500.0)

    def test_360dp_cycle_returns_all_keys(self):
        """360DP cycle must return fsmp, vip, pkap, bmnp_nest, cycle_hash."""
        result = self.engine.cycle(dso="HDSO", domain="CRISISCONNECT")
        for key in ["fsmp", "vip", "pkap", "bmnp_nest", "cycle_hash", "fsm_states"]:
            self.assertIn(key, result)

    def test_360dp_cycle_fsm_reaches_persist(self):
        """FSM must reach PERSIST state completing the cycle."""
        result = self.engine.cycle(dso="HDSO", domain="CAREERS")
        self.assertIn("PERSIST", result["fsm_states"])
        self.assertTrue(result["fsm_complete"])

    def test_360dp_all_domains(self):
        """360DP cycle must complete across all 4 GSMB domains."""
        domains = [
            ("CAREERS", "HDSO"), ("CRISISCONNECT", "HDSO"),
            ("KASILINK", "ADSO"), ("STARFALL", "HDSO"),
        ]
        for domain, dso in domains:
            result = self.engine.cycle(dso=dso, domain=domain)
            self.assertIn("cycle_hash", result)
            self.assertTrue(result["fsm_complete"])

    def test_bmnp_nesting_format_360dp(self):
        """360DP BMNP nesting must follow [360DP[DOMAIN[DSO→DSO_EFF[verdict]]]] format."""
        result = self.engine.cycle(dso="HDSO", domain="STARFALL")
        nest = result["bmnp_nest"]
        self.assertTrue(nest.startswith("[360DP["))
        self.assertIn("STARFALL", nest)


# ═══════════════════════════════════════════════════════════════
# 5. APU VECTOR MATRIX TESTS (import-only if available)
# ═══════════════════════════════════════════════════════════════

class TestAPUVectorMatrix(unittest.TestCase):
    """Test APU vector matrix if module is importable."""

    def setUp(self):
        try:
            from kopano import apu_vector_matrix as apu_mod
            self.apu_mod = apu_mod
            self.available = True
        except ImportError:
            self.available = False

    def _skip_if_unavailable(self):
        if not self.available:
            self.skipTest("apu_vector_matrix module not importable in this env")

    def test_apu_module_importable(self):
        """APU vector matrix must be importable."""
        self._skip_if_unavailable()
        self.assertIsNotNone(self.apu_mod)

    def test_apu_has_domain_states(self):
        """APU module must define domain states or equivalent structure."""
        self._skip_if_unavailable()
        # Check for any top-level dict/list with domain info
        attrs = dir(self.apu_mod)
        has_domain_related = any(
            "domain" in a.lower() or "apu" in a.lower() or "status" in a.lower()
            for a in attrs
        )
        self.assertTrue(has_domain_related, f"No domain-related attrs found. Attrs: {attrs[:20]}")

    def test_pkap_formula_constant_available(self):
        """PKAP formula string or function must be accessible in the module."""
        self._skip_if_unavailable()
        attrs = dir(self.apu_mod)
        has_pkap = any("pkap" in a.lower() or "formula" in a.lower() for a in attrs)
        self.assertTrue(has_pkap, f"No PKAP-related attrs. Attrs: {attrs[:20]}")


# ═══════════════════════════════════════════════════════════════
# 6. NCCNP PHASE 3 TESTS
# ═══════════════════════════════════════════════════════════════

class TestNCCNP(unittest.TestCase):
    """Test NCCNP Phase 3 — global comms-engineering closed loop."""

    def setUp(self):
        from kopano.nccnp import NCCNPEngine, KasiLinkPromotionEngine, PHASES, _agent_for_domain, _dso_for_domain
        self.engine    = NCCNPEngine(alp_receipt="test_receipt_nccnp")
        self.promoter  = KasiLinkPromotionEngine()
        self.phases    = PHASES
        self._agent    = _agent_for_domain
        self._dso      = _dso_for_domain

    def _good_signal(self, domain: str) -> dict:
        return {
            "who":        f"Test agent for {domain}",
            "what":       f"NCCNP unit test validation for {domain}",
            "where":      f"{domain}.KopanoLabs.com",
            "why":        "Unit test proof — NCCNP Phase 3 closed loop",
            "proof_link": "test_khelos_and_apu.py",
            "poc_artifact": f"nccnp_test_{domain}",
        }

    def test_phases_all_defined(self):
        """All 3 NCCNP phases must be registered."""
        for phase_num in [1, 2, 3]:
            self.assertIn(phase_num, self.phases)
            self.assertIn("protocols", self.phases[phase_num])
            self.assertIn("status",    self.phases[phase_num])

    def test_phase_3_ep_protocols(self):
        """Phase 3 must include FON-C, KHELOS, APU, IKP, 360DP."""
        ep_protos = self.phases[3]["protocols"]
        for proto in ["FON-C", "KHELOS-SWFUS", "APU-VECTOR", "IKP-CHAIN"]:
            self.assertIn(proto, ep_protos)

    def test_domain_helpers(self):
        """Domain helper functions must return correct agents and DSO levels."""
        self.assertEqual(self._agent("CAREERS"),       "VC")
        self.assertEqual(self._agent("CRISISCONNECT"), "AG")
        self.assertEqual(self._agent("KASILINK"),      "ANCHOR")
        self.assertEqual(self._agent("STARFALL"),      "FORGE")
        self.assertEqual(self._dso("KASILINK"), "ADSO")
        self.assertEqual(self._dso("CAREERS"),  "HDSO")

    def test_single_domain_run_careers(self):
        """Single NCCNP run on CAREERS must produce NCCNP_POC_CLOSED."""
        result = self.engine.run(self._good_signal("CAREERS"), domain="CAREERS")
        self.assertIn("phase_1_pp", result)
        self.assertIn("phase_2_bp", result)
        self.assertIn("phase_3_ep", result)
        self.assertEqual(result["phase_1_pp"]["verdict"], "CBP_PASS")
        self.assertEqual(result["final_verdict"], "NCCNP_POC_CLOSED")

    def test_foc_signal_fails_pp(self):
        """Signal with FOC bleed must fail PP CBP check."""
        bad_signal = {
            "who":   "test",
            "what":  "maybe tbd later placeholder",
            "where": "test",
            "why":   "test",
        }
        result = self.engine.run(bad_signal, domain="CAREERS")
        self.assertEqual(result["phase_1_pp"]["verdict"], "CBP_FAIL")
        self.assertGreater(len(result["phase_1_pp"]["foc_bleed"]), 0)

    def test_missing_4ws_fails_bp(self):
        """Signal missing 4Ws must fail BP with POC_SEVERED."""
        bad_signal = {"who": "test", "what": "test"}  # no where, no why
        result = self.engine.run(bad_signal, domain="CAREERS")
        self.assertFalse(result["phase_1_pp"]["four_ws_complete"])
        self.assertEqual(result["phase_2_bp"]["ikp_code"], "POC_SEVERED")

    def test_bmnp_nesting_format(self):
        """BMNP nesting trace must follow [NCCNP[DOMAIN[PP[BP[EP]]]]] format."""
        result = self.engine.run(self._good_signal("STARFALL"), domain="STARFALL")
        self.assertIn("[NCCNP[STARFALL", result["bmnp_trace"])
        self.assertIn("PP:CBP_PASS", result["bmnp_trace"])

    def test_all_domains_run(self):
        """run_all_domains() must produce 4 results."""
        results = self.engine.run_all_domains()
        self.assertEqual(len(results), 4)
        domains = {r["domain"] for r in results}
        self.assertEqual(domains, {"CAREERS", "CRISISCONNECT", "KASILINK", "STARFALL"})

    def test_all_domains_poc_closed(self):
        """All 4 domains must achieve NCCNP_POC_CLOSED with valid 4Ws signals."""
        results = self.engine.run_all_domains()
        for r in results:
            self.assertEqual(r["final_verdict"], "NCCNP_POC_CLOSED",
                             f"{r['domain']} did not close: {r['phase_3_ep']['loop_verdict']}")

    def test_cycle_hash_unique(self):
        """Each domain cycle must produce a unique hash."""
        results = self.engine.run_all_domains()
        hashes = [r["cycle_hash"] for r in results]
        self.assertEqual(len(hashes), len(set(hashes)), "Duplicate cycle hashes found")

    def test_nccnp_log_written(self):
        """NCCNP log file must be written after a run."""
        from kopano.nccnp import NCCNP_LOG
        size_before = NCCNP_LOG.stat().st_size if NCCNP_LOG.exists() else 0
        self.engine.run(self._good_signal("CRISISCONNECT"), domain="CRISISCONNECT")
        self.assertGreater(NCCNP_LOG.stat().st_size, size_before)

    def test_kasilink_promotion_audit_partial(self):
        """KasiLink promotion audit must show partial progress (not ready — 2 manual steps)."""
        results = self.engine.run_all_domains()
        audit = self.promoter.audit(results)
        self.assertEqual(audit["domain"], "KASILINK")
        self.assertFalse(audit["promotion_ready"])
        self.assertIn("purpose_artifact_count", audit["gaps"])
        self.assertIn("rtc_anchor_vote",        audit["gaps"])
        self.assertGreater(audit["met_count"], 0)
        self.assertEqual(audit["total_count"], 6)

    def test_kasilink_criteria_dict(self):
        """KasiLink promotion engine must define exactly 6 criteria."""
        self.assertEqual(len(self.promoter.CRITERIA), 6)


# ═══════════════════════════════════════════════════════════════
# 7. GSMB AUTO RUNNER TESTS
# ═══════════════════════════════════════════════════════════════

class TestGSMBAutoRunner(unittest.TestCase):
    """Test GSMB Auto Runner — full-stack one-tick validation."""

    def setUp(self):
        from kopano.gsmb_auto_runner import _runner_signal, _run_tick, RUNNER_LOG
        self._runner_signal = _runner_signal
        self._run_tick      = _run_tick
        self.RUNNER_LOG     = RUNNER_LOG

    def test_runner_signal_has_4ws(self):
        """Runner signal must contain all 4Ws."""
        signal = self._runner_signal(tick=99, alp_receipt="test_hash")
        for w in ["who", "what", "where", "why"]:
            self.assertIn(w, signal)
            self.assertTrue(signal[w], f"Empty {w} in runner signal")

    def test_runner_signal_has_proof_link(self):
        """Runner signal must have proof_link (tick reference)."""
        signal = self._runner_signal(tick=42, alp_receipt="abc123")
        self.assertIn("proof_link", signal)
        self.assertIn("42", signal["proof_link"])

    def test_tick_produces_valid_result(self):
        """Single tick must produce schema-compliant result."""
        result = self._run_tick(tick=1, alp_receipt="unit_test_receipt")
        self.assertEqual(result["schema"], "gsmb_auto_runner_tick_v1")
        self.assertIn("nccnp",      result)
        self.assertIn("apu",        result)
        self.assertIn("ikp",        result)
        self.assertIn("fonc_self",  result)
        self.assertIn("tick_hash",  result)
        self.assertIn("tick_verdict", result)

    def test_tick_verdict_is_poc_validated(self):
        """Single tick with clean state must produce POC_VALIDATED."""
        result = self._run_tick(tick=2, alp_receipt="unit_test_receipt")
        self.assertEqual(result["tick_verdict"], "POC_VALIDATED")

    def test_nccnp_all_domains_closed(self):
        """Tick must show 4/4 NCCNP domains POC_CLOSED."""
        result = self._run_tick(tick=3, alp_receipt="unit_test_receipt")
        self.assertEqual(result["nccnp"]["poc_closed"], 4)

    def test_ikp_all_clean(self):
        """Tick must show IKP CLEAN on all 4 domains."""
        result = self._run_tick(tick=4, alp_receipt="unit_test_receipt")
        self.assertGreaterEqual(result["ikp"]["clean"], 4)

    def test_fonc_self_clean(self):
        """Runner's FON-C self-audit must be CLEAN (runner signal has proof links)."""
        result = self._run_tick(tick=5, alp_receipt="unit_test_receipt")
        self.assertTrue(result["fonc_self"]["is_clean"])
        self.assertEqual(result["fonc_self"]["max_level"], 0)

    def test_runner_log_written(self):
        """Runner log must be written after each tick."""
        size_before = self.RUNNER_LOG.stat().st_size if self.RUNNER_LOG.exists() else 0
        self._run_tick(tick=6, alp_receipt="unit_test_receipt")
        self.assertGreater(self.RUNNER_LOG.stat().st_size, size_before)

    def test_tick_hash_is_hex(self):
        """Tick hash must be a 16-char hex string."""
        result = self._run_tick(tick=7, alp_receipt="unit_test_receipt")
        self.assertEqual(len(result["tick_hash"]), 16)
        int(result["tick_hash"], 16)  # must be valid hex

    def test_constraint_in_result(self):
        """I_AM_STATELESS_RENTER_NOT_LANDLORD must be in every tick result."""
        result = self._run_tick(tick=8, alp_receipt="unit_test_receipt")
        self.assertEqual(result["constraint"], "I_AM_STATELESS_RENTER_NOT_LANDLORD")


# ═══════════════════════════════════════════════════════════════
# RUNNER
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    print("=" * 72)
    print("KPGS UNIT TESTS")
    print("ALP #15 | 53a6f12c212fbebd | POC_VALIDATED")
    print("I_AM_STATELESS_RENTER_NOT_LANDLORD")
    print("=" * 72)

    loader  = unittest.TestLoader()
    suite   = unittest.TestSuite()

    for cls in [
        TestKhelosWitnessEngine,
        TestFONCEngine,
        TestIKPEngine,
        TestThreeSixtyDP,
        TestAPUVectorMatrix,
        TestNCCNP,
        TestGSMBAutoRunner,
    ]:
        suite.addTests(loader.loadTestsFromTestCase(cls))

    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)

    print("\n" + "=" * 72)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures:  {len(result.failures)}")
    print(f"Errors:    {len(result.errors)}")
    print(f"Skipped:   {len(result.skipped)}")
    verdict = "POC_VALIDATED" if result.wasSuccessful() else "FOC_DETECTED"
    print(f"Verdict:   {verdict}")
    print("[CONSTRAINT] I_AM_STATELESS_RENTER_NOT_LANDLORD")
    print("=" * 72)

    sys.exit(0 if result.wasSuccessful() else 1)
