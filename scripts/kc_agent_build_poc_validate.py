#!/usr/bin/env python3
"""Prove agent-building PoC without conflating governance outcomes with CI execution."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "kopano-core"))

from kopano.agent_build_poc_validate import validate_agent_build_poc  # noqa: E402
from kopano.ci_verdict_semantics import classify_agent_build_ci  # noqa: E402

REPORT_PATH = REPO / "docs" / "swarm-ops" / "AGENT_BUILD_POC_VALIDATION.json"
MAIN_BRAIN_LOG = REPO / "docs" / "swarm-ops" / "logs" / "KC Main Brain Log.jsonl"


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _persist(report: dict[str, object]) -> None:
    """Persist the CI-adapted receipt rather than the raw pre-adapter verdict."""

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    ci = report["ci"]
    assert isinstance(ci, dict)
    MAIN_BRAIN_LOG.parent.mkdir(parents=True, exist_ok=True)
    with MAIN_BRAIN_LOG.open("a", encoding="utf-8") as handle:
        handle.write(
            json.dumps(
                {
                    "schema": "kc_main_brain_log_v1",
                    "ts": _utc_now(),
                    "kind": "agent_build_poc_ci_adapter",
                    "summary": (
                        f"[AGENT_BUILD_POC] governance={ci['governance_verdict']} | "
                        f"execution={ci['execution_status']} | ci={ci['ci_status']} | "
                        f"external_evidence={ci['evidence_status']} | "
                        f"blocking={','.join(ci['blocking_failures']) or 'none'} | "
                        f"held={','.join(ci['held_external_evidence']) or 'none'}"
                    ),
                    "exit_code": ci["exit_code"],
                    "payload_ref": str(REPORT_PATH.relative_to(REPO)).replace("\\", "/"),
                },
                ensure_ascii=False,
            )
            + "\n"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-write", action="store_true", help="Skip report file + main brain")
    parser.add_argument("--json-only", action="store_true")
    args = parser.parse_args()

    # The core validator emits governance evidence only.  The adapter below is
    # the sole authority for mapping that receipt onto CI process status.
    raw_report = validate_agent_build_poc(write_report=False)
    ci = classify_agent_build_ci(raw_report)
    report = {**raw_report, "ci": ci}

    if not args.no_write:
        _persist(report)

    if args.json_only:
        print(json.dumps(report, indent=2))
    else:
        print(
            "VERDICT: "
            f"governance={ci['governance_verdict']} "
            f"execution={ci['execution_status']} "
            f"ci={ci['ci_status']}"
        )
        print(
            f"RAW: {raw_report['verdict']} "
            f"({raw_report['passed']}/{raw_report['total']})"
        )
        if ci["expected_declines"]:
            print(f"EXPECTED_DECLINE: {', '.join(ci['expected_declines'])}")
        if ci["held_external_evidence"]:
            print(f"HELD_EXTERNAL_EVIDENCE: {', '.join(ci['held_external_evidence'])}")
        if ci["blocking_failures"]:
            print(f"CI_BLOCKERS: {', '.join(ci['blocking_failures'])}")
        for check in raw_report["checks"]:
            mark = "ok" if check["verdict"] == "PASS" else "governed"
            print(f"  [{mark}] {check['check']}: {check.get('detail', '')[:80]}")
        print(f"\nReport: {REPORT_PATH.relative_to(REPO)}")

    return int(ci["exit_code"])


if __name__ == "__main__":
    raise SystemExit(main())
