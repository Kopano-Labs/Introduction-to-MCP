"""Count verified production rows in KC Review Log (not drill / steward theater)."""

from __future__ import annotations

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
REVIEW_LOG = REPO_ROOT / "docs" / "swarm-ops" / "logs" / "KC Review Log.jsonl"
DEFAULT_MIN = 10

_BYPASS = ("demo-bypass", "owner_proof=local_only")
_STEWARD_THEATER = (
    "apprenticeship steward:",
    "kc status checkpoint @",
    "checkpoint @",
)
_REPO_EVIDENCE = re.compile(
    r"https://github\.com/Kopano-Labs/Introduction-to-MCP/(actions|commit/|compare/)",
    re.I,
)


def _load_review_rows(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    rows: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        rows.append(json.loads(line))
    return rows


def is_verified_production(row: dict) -> bool:
    if row.get("role") != "student":
        return False
    phase = (row.get("phase") or "").lower()
    if phase in {"apprenticeship", "bootstrap", "system"}:
        return False
    if row.get("exit_code") != 0:
        return False
    summary = (row.get("summary") or "").lower()
    if row.get("agent_id") == "repo-seed" or "placeholder" in summary:
        return False
    if any(t in summary for t in _STEWARD_THEATER):
        return False
    urls = row.get("evidence_urls") or []
    if not urls:
        return False
    url_text = " ".join(urls).lower()
    if any(b in url_text for b in _BYPASS):
        return False
    if "github.com/" == url_text.strip() or url_text.rstrip("/") == "https://github.com":
        return False
    return bool(_REPO_EVIDENCE.search(" ".join(urls)))


def count_verified(path: Path | None = None) -> tuple[int, list[dict]]:
    log = path or REVIEW_LOG
    verified = [r for r in _load_review_rows(log) if is_verified_production(r)]
    return len(verified), verified


def check_minimum(min_required: int = DEFAULT_MIN, path: Path | None = None) -> tuple[bool, str]:
    n, rows = count_verified(path)
    if n >= min_required:
        return True, f"verified_production={n} (min {min_required})"
    return False, f"verified_production={n} need {min_required}; run: python scripts/kc_production_verify_run.py"


def main() -> int:
    import argparse

    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--min", type=int, default=DEFAULT_MIN)
    p.add_argument("--log", type=Path, default=None)
    args = p.parse_args()
    ok, msg = check_minimum(args.min, args.log)
    print(msg)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
