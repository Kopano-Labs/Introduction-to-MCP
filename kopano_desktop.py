#!/usr/bin/env python3
"""PyInstaller entry: Kopano Context desktop (API + Studio)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
for import_root in (ROOT / "kopano-core", ROOT):
    path = str(import_root)
    if import_root.exists() and path not in sys.path:
        sys.path.insert(0, path)

from kopano.runtime import configure_frozen_runtime  # noqa: E402

configure_frozen_runtime()

from kopano.desktop import main  # noqa: E402

if __name__ == "__main__":
    main()
