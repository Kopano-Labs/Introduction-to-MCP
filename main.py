#!/usr/bin/env python
"""Entry point for the active CLI surface during the rename transition."""

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent
IMPORT_ROOTS = [
    ROOT / "kopano-core",
    ROOT,
]

for import_root in IMPORT_ROOTS:
    import_root_str = str(import_root)
    if import_root.exists() and import_root_str not in sys.path:
        sys.path.insert(0, import_root_str)


try:
    from kopano.cli import app
except ImportError:
    from orch.orch.cli import app


def main():
    app()

if __name__ == "__main__":
    main()
