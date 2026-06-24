"""
test_evidence_bridge.py — Tests for CLAFP → CrisisConnect Evidence Bridge
==========================================================================
Verifies the evidence_bridge module correctly converts Altar gate results
into CrisisConnect-consumable evidence entries.

Constraint: I_AM_STATELESS_RENTER_NOT_LANDLORD
"""

import json
import os
import tempfile
from pathlib import Path

import pytest

from kopano.evidence_bridge import (
    altar_to_evidence,
    generate_evidence_payload,
    write_evidence_file,
)
from kopano.clafp_altar_core import CLAFPAltarCore


# ═══════════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════════

@pytest.fixture
def altar():
    return CLAFPAltarCore()


@pytest.fixture
def altar_result(altar):
    """Run a real Altar gate and get the result."""
    return altar.gate(
        signal="[VOC] GSMB governance evidence — kopano kpgs poc crisisconnect community",
        source="CF",
        core_result={
            "schema": "lacp_cycle_v1",
            "task_source": "CF",
            "cycle_verdict": "POC_VALIDATED",
            "cycle_hash": "test_hash_abc",
            "phases_poc": 22,
            "phases_total": 22,
            "ts_start": "2026-06-24T00:00:00Z",
            "constraint": "I_AM_STATELESS_RENTER_NOT_LANDLORD",
        },
    )


@pytest.fixture
def altar_results(altar_result):
    """List of altar results for batch tests."""
    return [altar_result]


# ═══════════════════════════════════════════════════════════════
# CONVERSION TESTS
# ═══════════════════════════════════════════════════════════════

class TestAltarToEvidence:
    """Test single Altar result → evidence entry conversion."""

    def test_returns_dict(self, altar_result):
        entry = altar_to_evidence(altar_result)
        assert isinstance(entry, dict)

    def test_has_required_fields(self, altar_result):
        entry = altar_to_evidence(altar_result)
        required = ["incident_id", "gate", "action", "verdict", "timestamp", "detail", "constraint"]
        for field in required:
            assert field in entry, f"Missing field: {field}"

    def test_gate_is_clafp_altar(self, altar_result):
        entry = altar_to_evidence(altar_result)
        assert entry["gate"] == "CLAFP_ALTAR"

    def test_verdict_is_poc_or_foc(self, altar_result):
        entry = altar_to_evidence(altar_result)
        assert entry["verdict"] in ("POC", "FOC")

    def test_poc_for_validated_altar(self, altar_result):
        entry = altar_to_evidence(altar_result)
        if altar_result["altar_verdict"] == "ALTAR_POC_VALIDATED":
            assert entry["verdict"] == "POC"

    def test_constraint_present(self, altar_result):
        entry = altar_to_evidence(altar_result)
        assert entry["constraint"] == "I_AM_STATELESS_RENTER_NOT_LANDLORD"

    def test_detail_is_json_parseable(self, altar_result):
        entry = altar_to_evidence(altar_result)
        detail = json.loads(entry["detail"])
        assert isinstance(detail, dict)
        assert "layers_pass" in detail
        assert "commandments" in detail
        assert "altar_hash" in detail

    def test_timestamp_present(self, altar_result):
        entry = altar_to_evidence(altar_result)
        assert len(entry["timestamp"]) > 0


# ═══════════════════════════════════════════════════════════════
# PAYLOAD GENERATION TESTS
# ═══════════════════════════════════════════════════════════════

class TestGenerateEvidencePayload:
    """Test batch evidence payload generation."""

    def test_returns_dict(self, altar_results):
        payload = generate_evidence_payload(altar_results)
        assert isinstance(payload, dict)

    def test_has_schema(self, altar_results):
        payload = generate_evidence_payload(altar_results)
        assert payload["schema"] == "crisisconnect_evidence_v1"

    def test_has_entries(self, altar_results):
        payload = generate_evidence_payload(altar_results)
        assert "entries" in payload
        assert len(payload["entries"]) == len(altar_results)

    def test_counts_poc_foc(self, altar_results):
        payload = generate_evidence_payload(altar_results)
        assert payload["poc_count"] + payload["foc_count"] == payload["total_entries"]

    def test_generated_timestamp(self, altar_results):
        payload = generate_evidence_payload(altar_results)
        assert "generated" in payload
        assert len(payload["generated"]) > 0

    def test_constraint(self, altar_results):
        payload = generate_evidence_payload(altar_results)
        assert payload["constraint"] == "I_AM_STATELESS_RENTER_NOT_LANDLORD"

    def test_empty_list(self):
        payload = generate_evidence_payload([])
        assert payload["total_entries"] == 0
        assert payload["entries"] == []

    def test_serializable_to_json(self, altar_results):
        payload = generate_evidence_payload(altar_results)
        json_str = json.dumps(payload, default=str)
        assert len(json_str) > 0
        reparsed = json.loads(json_str)
        assert reparsed["schema"] == "crisisconnect_evidence_v1"


# ═══════════════════════════════════════════════════════════════
# FILE WRITE TESTS
# ═══════════════════════════════════════════════════════════════

class TestWriteEvidenceFile:
    """Test evidence file output."""

    def test_writes_file(self, altar_results):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "evidence.json"
            result_path = write_evidence_file(altar_results, output=output)
            assert result_path.exists()

    def test_file_is_valid_json(self, altar_results):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "evidence.json"
            write_evidence_file(altar_results, output=output)
            with output.open() as f:
                data = json.load(f)
            assert data["schema"] == "crisisconnect_evidence_v1"

    def test_file_has_entries(self, altar_results):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "evidence.json"
            write_evidence_file(altar_results, output=output)
            with output.open() as f:
                data = json.load(f)
            assert len(data["entries"]) == len(altar_results)

    def test_overwrites_existing(self, altar_results):
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "evidence.json"
            write_evidence_file(altar_results, output=output)
            write_evidence_file(altar_results + altar_results, output=output)
            with output.open() as f:
                data = json.load(f)
            assert data["total_entries"] == len(altar_results) * 2


# ═══════════════════════════════════════════════════════════════
# INTEGRATION: Full pipeline
# ═══════════════════════════════════════════════════════════════

class TestIntegration:
    """Full pipeline: Altar → Bridge → JSON → parseable by frontend."""

    def test_full_pipeline(self, altar):
        """Run Altar, bridge to evidence, write JSON, verify frontend-ready."""
        result = altar.gate(
            signal="[VOC] Integration test — kopano kpgs governance community crisisconnect",
            source="CF",
            core_result={
                "schema": "lacp_cycle_v1",
                "task_source": "CF",
                "cycle_verdict": "POC_VALIDATED",
                "cycle_hash": "integration_test",
                "phases_poc": 22,
                "phases_total": 22,
                "ts_start": "2026-06-24T00:00:00Z",
                "constraint": "I_AM_STATELESS_RENTER_NOT_LANDLORD",
            },
        )

        # Convert
        entry = altar_to_evidence(result)
        assert entry["gate"] == "CLAFP_ALTAR"

        # Generate payload
        payload = generate_evidence_payload([result])
        assert payload["total_entries"] == 1

        # Write to temp file
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "evidence.json"
            write_evidence_file([result], output=output)

            # Verify frontend can parse
            with output.open() as f:
                frontend_data = json.load(f)

            assert frontend_data["schema"] == "crisisconnect_evidence_v1"
            assert len(frontend_data["entries"]) == 1
            assert frontend_data["entries"][0]["verdict"] in ("POC", "FOC")

    def test_multiple_altar_results(self, altar):
        """Multiple Altar results produce multiple evidence entries."""
        results = []
        for source in ["CF", "SSE", "RTC", "LACP", "GSMB_RUNNER"]:
            r = altar.gate(
                signal=f"[VOC] Multi-test {source} — kopano kpgs governance community",
                source=source,
                core_result={
                    "schema": "lacp_cycle_v1",
                    "task_source": source,
                    "cycle_verdict": "POC_VALIDATED",
                    "cycle_hash": f"multi_{source}",
                    "phases_poc": 22,
                    "phases_total": 22,
                    "ts_start": "2026-06-24T00:00:00Z",
                    "constraint": "I_AM_STATELESS_RENTER_NOT_LANDLORD",
                },
            )
            results.append(r)

        payload = generate_evidence_payload(results)
        assert payload["total_entries"] == 5
