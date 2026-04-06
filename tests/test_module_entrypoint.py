from typer.testing import CliRunner

from orch.__main__ import app


runner = CliRunner()


def test_python_m_orch_entrypoint_exposes_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Usage" in result.stdout
