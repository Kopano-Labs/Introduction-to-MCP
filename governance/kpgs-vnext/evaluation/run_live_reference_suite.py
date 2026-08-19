#!/usr/bin/env python3
"""Execute the KPGS reference suite and feed real receipts into the profiler.

This is a CI/regression live workflow, not production telemetry. Deterministic
cases execute their repository fixtures; the probabilistic case consumes a
versioned regression sample window. The resulting canonical evidence bundle is
then scored by the existing evaluation/profiler engine.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
EVALUATION_DIR = ROOT / "governance/kpgs-vnext/evaluation"
EVIDENCE_PATH = ROOT / "governance/kpgs-vnext/evidence/evidence.py"
EVALUATION_PATH = EVALUATION_DIR / "evaluation.py"
SUITE_PATH = EVALUATION_DIR / "reference-suite.json"
POLICY_PATH = EVALUATION_DIR / "promotion-policy.json"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _repo_path(ref: str) -> Path:
    if not ref.startswith("repo://"):
        raise ValueError(f"reference is not repository-local: {ref}")
    path = (ROOT / ref.removeprefix("repo://")).resolve()
    if ROOT.resolve() not in path.parents and path != ROOT.resolve():
        raise ValueError(f"fixture escapes repository root: {ref}")
    if not path.exists():
        raise FileNotFoundError(path)
    return path


def _command_for_fixture(path: Path) -> list[str]:
    relative = path.relative_to(ROOT).as_posix()
    if path.suffix == ".py" and path.parent == ROOT / "tests":
        return [
            sys.executable,
            "-m",
            "unittest",
            "discover",
            "-s",
            "tests",
            "-p",
            path.name,
            "-v",
        ]
    if path.suffix == ".csproj":
        return ["dotnet", "run", "--project", relative, "-c", "Release"]
    raise ValueError(f"unsupported deterministic fixture: {relative}")


def _execute(command: list[str]) -> dict[str, Any]:
    started = time.perf_counter()
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    duration_ms = round((time.perf_counter() - started) * 1000, 3)
    combined = (completed.stdout or "") + (completed.stderr or "")
    return {
        "command": command,
        "returncode": completed.returncode,
        "duration_ms": duration_ms,
        "output_sha256": _sha256_bytes(combined.encode("utf-8")),
        "output_tail": combined[-2000:],
    }


def _adapter_version() -> str:
    project = ROOT / "dotnet/Kopano.Kpgs.Adapter/Kopano.Kpgs.Adapter.csproj"
    tree = ET.parse(project)
    version = tree.findtext(".//Version")
    return (version or "0.0.0-unversioned").strip()


def _skill_identity() -> tuple[str, str, str]:
    manifest = json.loads(
        (
            ROOT
            / "governance/kpgs-vnext/skills/core/kpgs-audit-verify-govern/skill.json"
        ).read_text(encoding="utf-8")
    )
    return (
        str(manifest["name"]),
        str(manifest["version"]),
        str(manifest["runtime"]["renter_protocol"]),
    )


def _commit_sha() -> str:
    candidate = os.getenv("GITHUB_SHA", "").strip()
    if len(candidate) == 40:
        return candidate
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    return result.stdout.strip()


def _utc_now() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def run(output_path: Path) -> dict[str, Any]:
    evaluation = _load_module("kpgs_live_evaluation", EVALUATION_PATH)
    evidence = _load_module("kpgs_live_evidence", EVIDENCE_PATH)

    suite = evaluation.load_json(SUITE_PATH)
    policy = evaluation.load_json(POLICY_PATH)
    results = []
    executions: dict[str, dict[str, Any]] = {}

    for case in suite["cases"]:
        case_id = str(case["id"])
        fixture_path = _repo_path(str(case["fixture_ref"]))
        method = str(case["method"])

        if method == "deterministic":
            execution = _execute(_command_for_fixture(fixture_path))
            score = 1.0 if execution["returncode"] == 0 else 0.0
            executions[case_id] = {
                **execution,
                "fixture_ref": case["fixture_ref"],
                "classification": "EXECUTED_REPOSITORY_FIXTURE",
            }
            results.append(
                evaluation.EvaluationResult(
                    case_id=case_id,
                    method=method,
                    score=score,
                    sample_size=1,
                    evidence_ref=f"ci://evaluation/{case_id}/{execution['output_sha256']}",
                    verifier="ci://evaluation-reference-suite",
                )
            )
            continue

        if method == "probabilistic":
            fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
            samples = [float(value) for value in fixture.get("samples", [])]
            if not samples:
                raise RuntimeError(f"probabilistic fixture has no samples: {fixture_path}")
            score = sum(samples) / len(samples)
            executions[case_id] = {
                "fixture_ref": case["fixture_ref"],
                "fixture_sha256": _sha256_file(fixture_path),
                "classification": fixture.get("classification"),
                "sample_size": len(samples),
                "score": score,
            }
            results.append(
                evaluation.EvaluationResult(
                    case_id=case_id,
                    method=method,
                    score=score,
                    sample_size=len(samples),
                    evidence_ref=f"repo://{fixture_path.relative_to(ROOT).as_posix()}",
                    verifier="ci://evaluation-reference-suite",
                )
            )
            continue

        raise RuntimeError(f"live runner has no governed fixture adapter for {method}")

    evidence_refs = {
        "trace_ref": "ci://evaluation/reference-suite/trace",
        "task_ref": "task://kpgs-core-regression",
        "spec_ref": "repo://governance/kpgs-vnext/evaluation/reference-suite.json",
        "skill_ref": "repo://governance/kpgs-vnext/skills/core/kpgs-audit-verify-govern/skill.json",
        "renter_ref": "repo://governance/kpgs-vnext/security/capability_lease.py",
        "verifier_ref": "ci://evaluation-reference-suite",
    }
    evaluation_result = evaluation.evaluate_run(
        suite=suite,
        results=results,
        evidence_refs=evidence_refs,
        governance_admitted=True,
    )

    commit_sha = _commit_sha()
    run_id = os.getenv("GITHUB_RUN_ID", "local")
    skill_name, skill_version, renter_protocol = _skill_identity()
    correlation_id = f"evaluation:{commit_sha[:12]}"
    builder = evidence.EvidenceBundleBuilder(
        estate_property="kopanolabs.com",
        release_ref=f"ci://github-actions/{run_id}",
        commit_sha=commit_sha,
        adapter={
            "implementation": "Kopano.Kpgs.Adapter",
            "version": _adapter_version(),
            "protocol_version": "1.0",
        },
        renter={
            "renter_id": "ci:reference-renter",
            "protocol_version": renter_protocol,
        },
        skills=[{"name": skill_name, "version": skill_version}],
        task_id="kpgs-core-regression",
        session_id=f"ci:{run_id}",
        correlation_id=correlation_id,
        governing_spec_ref="repo://governance/kpgs-vnext/evaluation/README.md",
        retention_policy_ref="policy://kpgs/evaluation-ci-retention",
        redaction_policy_ref="policy://kpgs/evaluation-ci-redaction",
    )
    builder.add_capability_lease_ref(
        f"ci://evaluation/renter-capability-denial/{commit_sha}"
    )

    now = _utc_now()
    deterministic = [
        result for result in results if result.method == "deterministic"
    ]
    by_id = {result.case_id: result for result in results}
    trace_status = lambda case_id: (
        "succeeded" if by_id[case_id].score >= 1.0 else "failed"
    )
    builder.add_trace_hop(
        layer="pwa",
        ref="ci://evaluation/reference-client",
        status="succeeded",
        at=now,
        metadata={"classification": "CI_REFERENCE_PATH_NOT_PRODUCTION_PWA"},
    )
    builder.add_trace_hop(
        layer="adapter",
        ref=f"ci://evaluation/dotnet-adapter/{commit_sha}",
        status=trace_status("dotnet-adapter-replay-lease-boundary"),
        at=now,
        duration_ms=executions["dotnet-adapter-replay-lease-boundary"]["duration_ms"],
    )
    builder.add_trace_hop(
        layer="sovereign-hub",
        ref=f"ci://evaluation/capability-authority/{commit_sha}",
        status=trace_status("renter-capability-denial"),
        at=now,
    )
    builder.add_trace_hop(
        layer="renter",
        ref=f"ci://evaluation/renter/{commit_sha}",
        status=trace_status("renter-capability-denial"),
        at=now,
        duration_ms=executions["renter-capability-denial"]["duration_ms"],
    )
    builder.add_trace_hop(
        layer="skill",
        ref=f"ci://evaluation/skill/{commit_sha}",
        status=trace_status("skill-lease-bound-execution"),
        at=now,
        duration_ms=executions["skill-lease-bound-execution"]["duration_ms"],
    )
    builder.add_trace_hop(
        layer="verifier",
        ref="ci://evaluation-reference-suite",
        status="succeeded" if evaluation_result.hard_gates_passed else "failed",
        at=now,
    )

    suite_ref = "repo://governance/kpgs-vnext/evaluation/reference-suite.json"
    user_fixture_ref = "repo://governance/kpgs-vnext/evaluation/fixtures/adaptive-user-outcome.json"
    builder.add_artifact(
        kind="specification", ref=suite_ref, sha256=_sha256_file(SUITE_PATH)
    )
    builder.add_artifact(
        kind="capability-lease",
        ref="repo://tests/test_capability_lease_runtime.py",
        sha256=_sha256_file(ROOT / "tests/test_capability_lease_runtime.py"),
    )
    builder.add_artifact(
        kind="execution",
        ref="repo://dotnet/Kopano.Kpgs.Adapter.Tests/Kopano.Kpgs.Adapter.Tests.csproj",
        sha256=_sha256_file(
            ROOT
            / "dotnet/Kopano.Kpgs.Adapter.Tests/Kopano.Kpgs.Adapter.Tests.csproj"
        ),
    )
    result_digest = _sha256_bytes(
        json.dumps(
            [
                {
                    "case_id": result.case_id,
                    "method": result.method,
                    "score": result.score,
                    "sample_size": result.sample_size,
                    "evidence_ref": result.evidence_ref,
                    "verifier": result.verifier,
                }
                for result in results
            ],
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    )
    builder.add_artifact(
        kind="verification",
        ref=f"ci://evaluation/reference-suite/results/{result_digest}",
        sha256=result_digest,
    )
    user_fixture_path = _repo_path(user_fixture_ref)
    builder.add_artifact(
        kind="user-outcome",
        ref=user_fixture_ref,
        sha256=_sha256_file(user_fixture_path),
    )

    for result in results:
        method = (
            "integration"
            if result.case_id == "dotnet-adapter-replay-lease-boundary"
            else "unit"
            if result.method == "deterministic"
            else "integration"
        )
        builder.add_verification(
            verifier_id="ci://evaluation-reference-suite",
            criterion_id=result.case_id,
            method=method,
            hard_gate=bool(
                next(case["hard_gate"] for case in suite["cases"] if case["id"] == result.case_id)
            ),
            passed=result.passed,
            evidence_ref=result.evidence_ref,
            score=result.score,
        )

    probabilistic = by_id["adaptive-user-outcome"]
    hard_pass_ratio = (
        sum(1 for result in deterministic if result.passed) / len(deterministic)
    )
    builder.add_metric(
        name="task-completion",
        value=probabilistic.score,
        unit="ratio",
        evidence_ref=probabilistic.evidence_ref,
    )
    builder.add_metric(
        name="reliability",
        value=hard_pass_ratio,
        unit="ratio",
        evidence_ref="ci://evaluation/deterministic-pass-ratio",
    )
    builder.add_metric(
        name="error-rate",
        value=1.0 - hard_pass_ratio,
        unit="ratio",
        evidence_ref="ci://evaluation/deterministic-error-ratio",
    )
    builder.set_aggregate_score("deterministic", evaluation_result.deterministic_score)
    builder.set_aggregate_score("probabilistic", evaluation_result.probabilistic_score)
    builder.set_aggregate_score("model", evaluation_result.model_score)

    governance_decision = "allow" if evaluation_result.hard_gates_passed else "hold"
    bundle = builder.finalize(
        decision=governance_decision,
        reason=(
            "Executed CI regression evidence is admitted for profiler evaluation; this is not a release promotion."
            if governance_decision == "allow"
            else "One or more executed deterministic hard gates failed; profiler must hold."
        ),
        decision_ref=f"ci://github-actions/{run_id}/evaluation",
        next_action="Apply promotion policy; high-risk release still requires human approval.",
    )
    engineering = evidence.engineering_scorecard(bundle)
    decision = evaluation.decide_promotion(
        evaluation=evaluation_result,
        policy=policy,
        evidence_bundle=bundle,
        human_approval_ref=None,
    )
    profile = evaluation.profile_evaluation(evaluation_result, decision)

    payload = {
        "schema": "kpgs.evaluation-live-reference-receipt.v1",
        "classification": "CI_REGRESSION_EXECUTION_NOT_PRODUCTION_TELEMETRY",
        "commit_sha": commit_sha,
        "suite_id": suite["suite_id"],
        "suite_version": suite["version"],
        "executions": executions,
        "evaluation": {
            "hard_gates_passed": evaluation_result.hard_gates_passed,
            "deterministic_score": evaluation_result.deterministic_score,
            "probabilistic_score": evaluation_result.probabilistic_score,
            "model_score": evaluation_result.model_score,
            "evidence_refs": evaluation_result.evidence_refs,
        },
        "evidence_bundle": bundle,
        "engineering_scorecard": engineering,
        "profile": profile,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    # The suite is high-risk. Even with every executable regression green, an
    # unattended CI run must HOLD rather than manufacture human approval.
    if not evaluation_result.hard_gates_passed:
        raise SystemExit("executed deterministic hard gate failed")
    if decision.recommendation != evaluation.Recommendation.HOLD:
        raise SystemExit("high-risk CI evaluation unexpectedly bypassed human approval HOLD")
    if "human approval" not in " ".join(decision.reasons).lower():
        raise SystemExit("high-risk HOLD did not identify missing human approval")
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "artifacts/evaluation-live-reference.json",
    )
    args = parser.parse_args(argv)
    payload = run(args.output)
    print(
        "KPGS evaluation live reference PASS: "
        f"bundle={payload['evidence_bundle']['bundle_id']} "
        f"recommendation={payload['profile']['recommendation']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
