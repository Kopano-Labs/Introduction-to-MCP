"""Tests for scripts/kc_verified_production.py."""

from __future__ import annotations

import json
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from kc_verified_production import is_verified_production  # noqa: E402


def test_drill_row_not_verified() -> None:
    row = {
        "role": "student",
        "phase": "apprenticeship",
        "exit_code": 0,
        "summary": "KCA-0001 done",
        "evidence_urls": [
            "https://github.com/Kopano-Labs/Introduction-to-MCP/actions",
        ],
    }
    assert not is_verified_production(row)


def test_production_row_verified() -> None:
    row = {
        "role": "student",
        "phase": "production",
        "exit_code": 0,
        "summary": "P01: pytest kc_log_append",
        "evidence_urls": [
            "https://github.com/Kopano-Labs/Introduction-to-MCP/compare/master...x",
            "https://github.com/Kopano-Labs/Introduction-to-MCP/actions",
        ],
    }
    assert is_verified_production(row)


def test_checkpoint_theater_not_verified() -> None:
    row = {
        "role": "student",
        "phase": "audit",
        "exit_code": 0,
        "summary": "kc status checkpoint @ 50",
        "evidence_urls": [
            "https://github.com/Kopano-Labs/Introduction-to-MCP/actions",
        ],
    }
    assert not is_verified_production(row)


def test_count_from_fixture(tmp_path: Path) -> None:
    log = tmp_path / "review.jsonl"
    rows = [
        {
            "role": "student",
            "phase": "production",
            "exit_code": 0,
            "summary": f"P{i:02d}: ok",
            "evidence_urls": [
                "https://github.com/Kopano-Labs/Introduction-to-MCP/commit/abc",
                "https://github.com/Kopano-Labs/Introduction-to-MCP/actions",
            ],
        }
        for i in range(10)
    ]
    log.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
    from kc_verified_production import check_minimum  # noqa: E402

    ok, msg = check_minimum(10, log)
    assert ok, msg
