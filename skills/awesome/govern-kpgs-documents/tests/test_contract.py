from __future__ import annotations

import runpy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = runpy.run_path(str(ROOT / "scripts" / "validate_package.py"))


def test_kpgs_dts_package_contract() -> None:
    errors = VALIDATOR["validate_package"](ROOT)
    assert errors == []


def test_graduation_requires_verified_production() -> None:
    manifest = {
        "schema": "kpgs_document_manifest_v1",
        "document_id": "TEST-001",
        "canonical_id": "test_document",
        "title": "Test",
        "version": "1.0.0",
        "status": "graduated",
        "proof_state": "poc",
        "owner": "owner",
        "author": "author",
        "source": {"repository": "owner/repo", "ref": "abc"},
        "authority_class": "repo_canonical",
        "evidence_class": "verified-source",
        "kpefs": {"primary_vector": "V4_DIASPORA", "secondary_vectors": []},
        "protocols": [],
        "promotion_gate": {"requires": ["PROOF-01", "PROOF-02", "PROOF-03"]},
        "linked_evidence": [],
        "renter_assertion": "I_AM_STATELESS_RENTER_NOT_LANDLORD",
    }
    errors = VALIDATOR["validate_document_manifest"](manifest)
    assert "document manifest: graduated requires verified_production proof_state" in errors


def test_indexed_publication_requires_discovery_receipt() -> None:
    manifest = {
        "schema": "kpgs_document_manifest_v1",
        "document_id": "TEST-002",
        "canonical_id": "publication_test",
        "title": "Publication Test",
        "version": "1.0.0",
        "status": "operating",
        "proof_state": "poc",
        "owner": "owner",
        "author": "author",
        "source": {"repository": "owner/repo", "ref": "abc"},
        "authority_class": "repo_canonical",
        "evidence_class": "verified-source",
        "kpefs": {"primary_vector": "V4_DIASPORA", "secondary_vectors": []},
        "protocols": [],
        "promotion_gate": {"requires": ["PROOF-01", "PROOF-02", "PROOF-03"]},
        "linked_evidence": [],
        "publication": {"state": "indexed", "discovery_receipt": None},
        "renter_assertion": "I_AM_STATELESS_RENTER_NOT_LANDLORD",
    }
    errors = VALIDATOR["validate_document_manifest"](manifest)
    assert "document manifest: indexed publication requires discovery_receipt" in errors
