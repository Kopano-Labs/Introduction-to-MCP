"""
Pytest tests for the orch CLI application.
"""
import pytest
from typer.testing import CliRunner
from unittest.mock import patch

from orch.orch.cli import app
from orch.orch.agent_manager import Agent

runner = CliRunner()


def test_agents_list_no_agents():
    """
    Test `orch agents list` when no agents are configured.
    """
    with patch('orch.orch.cli.load_agents', return_value={}):
        result = runner.invoke(app, ["agents", "list"])
        assert result.exit_code == 0
        assert "No agents configured yet." in result.stdout


def test_agents_list_with_agents():
    """
    Test `orch agents list` with a configured agent.
    """
    mock_agent = Agent(id="gemini-test", provider="google", model="gemini-pro", api_key="mock-key", persona="")
    with patch('orch.orch.cli.load_agents', return_value={"gemini-test": mock_agent}):
        result = runner.invoke(app, ["agents", "list"])
        assert result.exit_code == 0
        assert "Configured Agents" in result.stdout
        assert "gemini-test" in result.stdout
        assert "google" in result.stdout


def test_agents_config_new_agent():
    """
    Test `orch agents config` correctly saves a new agent.
    """
    with patch('orch.orch.cli.load_agents', return_value={}), \
         patch('orch.orch.cli.save_agents') as mock_save:

        agent_id = "test-gpt"
        provider = "openai"
        model = "gpt-4o"
        api_key = "sk-12345"
        persona = "A helpful assistant."

        result = runner.invoke(app, [
            "agents", "config", agent_id,
            "--provider", provider,
            "--model", model,
            "--api-key", api_key,
            "--persona", persona,
        ])

        assert result.exit_code == 0
        assert f"Agent '{agent_id}' configured successfully." in result.stdout

        mock_save.assert_called_once()
        saved_agents = mock_save.call_args[0][0]

        assert agent_id in saved_agents
        new_agent = saved_agents[agent_id]
        assert new_agent.id == agent_id
        assert new_agent.provider == provider
        assert new_agent.model == model
        assert new_agent.api_key == api_key
        assert new_agent.persona == persona