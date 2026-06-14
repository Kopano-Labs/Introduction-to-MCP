"""Operating mesh — flagship assignments and promotion chain."""

from __future__ import annotations

import pytest

from kopano.operating_mesh import (
    FLAGSHIP_ASSIGNMENTS,
    lint_bracket_text,
    operating_mesh_status,
    promote_flagship,
)


@pytest.mark.integration
def test_flagship_assignments_count():
    assert len(FLAGSHIP_ASSIGNMENTS) == 10
    assert "ama_phu_entertainment" in FLAGSHIP_ASSIGNMENTS
    assert FLAGSHIP_ASSIGNMENTS["ama_phu_entertainment"]["department"] == "ama_phu_creativity"


@pytest.mark.integration
def test_bracket_lint_rejects_sacred_caps():
    out = lint_bracket_text("[ONE_WORLD_ORDER] summary")
    assert out["ok"] is False
    assert out["violations"]


@pytest.mark.integration
def test_operating_mesh_status_shape():
    st = operating_mesh_status()
    assert st["flagships_total"] == 10
    assert len(st["flagships"]) == 10
    assert "eddie_bgf_mining" in FLAGSHIP_ASSIGNMENTS


@pytest.mark.integration
def test_promote_one_flagship():
    sid = "freddy_nw_alfalfa"
    out = promote_flagship(sid, skip_if_operating=False, run_department_begin=True)
    assert out.get("sub_brain_id") == sid
    assert out.get("proofs", {}).get("PROOF-01_blackmask_ship") is True
    assert out.get("proofs", {}).get("PROOF-02_teacher_approve") is True
    assert out.get("status") == "operating"
    assert out.get("poc_verdict") == "PASS"
