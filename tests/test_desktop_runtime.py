"""Desktop runtime helpers (non-frozen)."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "kopano-core"))

from kopano.runtime import configure_frozen_runtime, default_db_path, is_frozen_runtime  # noqa: E402


def test_not_frozen_by_default():
    assert is_frozen_runtime() is False
    configure_frozen_runtime()  # no-op when not frozen


def test_default_db_path_under_localappdata():
    path = default_db_path()
    assert path.name == "datalake.db"
    assert path.parent.name == "KopanoContext"
