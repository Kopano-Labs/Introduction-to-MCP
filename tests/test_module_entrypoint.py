
import sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "kopano-core"))

from typer.testing import CliRunner

from kopano.__main__ import app


runner = CliRunner()


def test_python_m_orch_entrypoint_exposes_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Usage" in result.stdout
