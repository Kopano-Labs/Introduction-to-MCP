"""Dependency-free validator for KPGS evidence bundles and scorecards."""

from __future__ import annotations

from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
SCHEMA = HERE / "evidence-bundle.schema.json"
RUNTIME = HERE / "evidence.py"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"KPGS-EVIDENCE FAIL: {message}")


def load_runtime():
    spec = importlib.util.spec_from_file_location("kpgs_evidence_validator_runtime", RUNTIME)
    require(spec is not None and spec.loader is not None, "evidence runtime cannot load")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    required = set(schema.get("required", []))
    for field_name in (
        "commit_sha",
        "trace_hops",
        "metrics",
        "retention_policy_ref",
        "redaction_policy_ref",
    ):
        require(field_name in required, f"bundle contract lost {field_name}")

    trace_layers = set(
        schema["properties"]["trace_hops"]["items"]["properties"]["layer"]["enum"]
    )
    require(
        {"pwa", "adapter", "sovereign-hub", "renter", "skill", "verifier", "deployment"}
        <= trace_layers,
        "cross-layer trace vocabulary is incomplete",
    )
    decision_enum = set(
        schema["properties"]["governance_decision"]["properties"]["decision"]["enum"]
    )
    require(
        {"allow", "deny", "promote", "rollback", "hold"} == decision_enum,
        "governance decision vocabulary drifted",
    )

    runtime = load_runtime()
    fixed_now = datetime(2026, 8, 18, 10, 15, tzinfo=timezone.utc)
    builder = runtime.EvidenceBundleBuilder(
        estate_property="FivesArena.com",
        release_ref="release://validator/fivesarena",
        commit_sha="b" * 40,
        adapter={"implementation": "canonical-domain-adapter", "version": "v1"},
        renter={"renter_id": "renter:validator", "protocol_version": "1.0"},
        skills=[{"name": "validator-skill", "version": "1.0.0"}],
        task_id="task:validator",
        session_id="session:validator",
        correlation_id="corr:validator",
        governing_spec_ref="spec://validator/evidence/v1",
        retention_policy_ref="retention://validator/release/v1",
        redaction_policy_ref="redaction://validator/no-secrets/v1",
        clock=lambda: fixed_now,
    )
    builder.add_capability_lease_ref("lease://validator/001")
    for index, layer in enumerate(
        ["pwa", "adapter", "sovereign-hub", "renter", "skill"]
    ):
        builder.add_trace_hop(
            layer=layer,
            ref=f"{layer}://validator/{index}",
            status="succeeded",
            at=f"2026-08-18T10:15:0{index}Z",
        )
    builder.add_trace_hop(
        layer="verifier",
        ref="verifier:validator",
        status="succeeded",
        at="2026-08-18T10:15:06Z",
    )
    builder.add_trace_hop(
        layer="deployment",
        ref="deployment://validator/001",
        status="succeeded",
        at="2026-08-18T10:15:07Z",
    )
    for kind in runtime.PROMOTION_ARTIFACT_KINDS:
        builder.add_artifact(kind=kind, ref=f"evidence://validator/{kind}")
    metric_values = {
        "latency": 100.0,
        "realtime-health": True,
        "reliability": 0.999,
        "error-rate": 0.001,
        "task-completion": 0.95,
        "task-abandonment": 0.05,
        "accessibility": True,
        "mobile": True,
    }
    for name, value in metric_values.items():
        builder.add_metric(
            name=name,
            value=value,
            evidence_ref=f"metric://validator/{name}",
        )
    builder.add_verification(
        verifier_id="verifier:validator",
        criterion_id="release-hard-gate",
        method="security",
        hard_gate=True,
        passed=True,
        evidence_ref="verification://validator/hard-gate",
        score=1.0,
    )
    bundle = builder.finalize(
        decision="promote",
        reason="Validator evidence surface is complete and hard gates pass.",
        decision_ref="decision://validator/promote",
    )
    require(bundle["commit_sha"] == "b" * 40, "exact commit provenance drifted")
    engineering = runtime.engineering_scorecard(bundle)
    everyday = runtime.everyday_scorecard(bundle)
    require(
        engineering["bundle_id"] == everyday["bundle_id"] == bundle["bundle_id"],
        "scorecards do not derive from one canonical bundle",
    )
    require(engineering["hard_gate_clear"] is True, "passing hard gate was lost")
    require(everyday["status"] == "ready", "plain governance view drifted")
    recommendation = runtime.rollback_recommendation(bundle)
    require(not recommendation["triggered"], "clean release triggered rollback")
    require(
        recommendation["automatic_execution"] is False,
        "evidence runtime gained rollback execution authority",
    )

    print(
        "KPGS-EVIDENCE PASS: exact release correlation, secret-safe evidence, "
        "non-averaged hard gates and shared scorecards are executable."
    )


if __name__ == "__main__":
    main()
