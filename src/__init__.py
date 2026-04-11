from pathlib import Path

_PACKAGE_ROOT = Path(__file__).resolve().parent
_TARGET_ROOT = (
    _PACKAGE_ROOT.parent
    / "Schematics"
    / "06-Reference"
    / "kopano-code-implementation"
    / "src"
)

__path__ = [str(_TARGET_ROOT)]

