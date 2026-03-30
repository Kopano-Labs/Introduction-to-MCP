"""
Pytest tests for the orch CLI application.
"""
import pytest
import sqlite3
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock

from orch.orch.cli import app
from orch.orch.agent_manager import Agent

runner = CliRunner()

@pytest.fixture
def in_memory_db():
    """
    Pytest fixture to create and manage an in-memory SQLite database for testing.
    It creates the schema and patches get_db_connection to use this in-memory DB.
    """
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    # Create schema from database.py
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS discussions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic TEXT NOT NULL,
        start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        discussion_id INTEGER NOT NULL,
        round_num INTEGER NOT NULL,
        agent_id TEXT NOT NULL,
        agent_model TEXT NOT NULL,
        prompt TEXT,
        response TEXT NOT NULL,
        is_moderator_direction INTEGER NOT NULL DEFAULT 0,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (discussion_id) REFERENCES discussions (id)
    );
    """)
    conn.commit()

    with patch('orch.orch.cli.get_db_connection', return_value=conn):
        yield conn

    conn.close()


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


def test_serve_launch_with_logging(in_memory_db):
    """
    Test that `orch serve launch` correctly logs the discussion to the database.
    This verifies capability #98: Explain its own reasoning via audit trails.
    """
    # Mock agents
    mock_agent = Agent(id="test-agent", provider="test", model="test-model", api_key="test-key", persona="")
    mock_mod_agent = Agent(id="mod-agent", provider="test", model="mod-model", api_key="test-key", persona="")

    # Mock the message object that generate_response returns
    mock_message = MagicMock()
    mock_message.content = "This is a test response."

    with patch('orch.orch.cli.load_agents', return_value={"test-agent": mock_agent, "mod-agent": mock_mod_agent}), \
         patch('orch.orch.agent_manager.Agent.generate_response', return_value=mock_message), \
         patch('orch.orch.moderator.Moderator.moderate', return_value="This is a moderator direction."):

        # Run the command for 2 rounds to ensure the moderator is triggered
        result = runner.invoke(app, [
            "serve", "launch",
            "--topic", "Test Logging",
            "--agents", "test-agent",
            "--moderator", "mod-agent",
            "--max-rounds", "2"
        ], catch_exceptions=False)

        assert result.exit_code == 0
        assert "Discussion Ended" in result.stdout

        # Verify database entries
        cursor = in_memory_db.cursor()

        # Check discussion table
        cursor.execute("SELECT * FROM discussions")
        discussions = cursor.fetchall()
        assert len(discussions) == 1
        assert discussions[0]['topic'] == "Test Logging"
        discussion_id = discussions[0]['id']

        # Check messages table
        cursor.execute("SELECT * FROM messages WHERE discussion_id = ? ORDER BY id ASC", (discussion_id,))
        messages = cursor.fetchall()

        # Expect 3 messages: Agent (R1), Moderator (R2), Agent (R2)
        assert len(messages) == 3

        # Message 1: Agent in round 1
        assert messages[0]['agent_id'] == 'test-agent' and messages[0]['is_moderator_direction'] == 0
        assert messages[0]['prompt'] == 'Test Logging'
        # Message 2: Moderator in round 2
        assert messages[1]['agent_id'] == 'mod-agent' and messages[1]['is_moderator_direction'] == 1
        # Message 3: Agent in round 2, prompted by moderator
        assert messages[2]['agent_id'] == 'test-agent' and messages[2]['is_moderator_direction'] == 0
        assert messages[2]['prompt'] == 'This is a moderator direction.'


def test_serve_launch_context_handling(in_memory_db):
    """
    Test that `orch serve launch` correctly manages and passes `full_conversation_history`
    to agents and the moderator.
    """
    # Mock agents
    mock_agent = Agent(id="test-agent", provider="test", model="test-model", api_key="test-key", persona="")
    mock_mod_agent = Agent(id="mod-agent", provider="test", model="mod-model", api_key="test-key", persona="")

    # Mock responses for agent and moderator
    mock_agent_response_r1 = MagicMock()
    mock_agent_response_r1.content = "Agent 1 Round 1 Response"
    mock_agent_response_r2 = MagicMock()
    mock_agent_response_r2.content = "Agent 1 Round 2 Response"
    mock_moderator_direction_r2 = "Moderator Round 2 Direction"

    with patch('orch.orch.cli.load_agents', return_value={"test-agent": mock_agent, "mod-agent": mock_mod_agent}), \
         patch('orch.orch.agent_manager.Agent.generate_response', side_effect=[mock_agent_response_r1, mock_agent_response_r2]) as mock_agent_generate_response, \
         patch('orch.orch.moderator.Moderator.moderate', return_value=mock_moderator_direction_r2) as mock_moderator_moderate:

        topic = "Test Context Handling"
        result = runner.invoke(app, [
            "serve", "launch",
            "--topic", topic,
            "--agents", "test-agent",
            "--moderator", "mod-agent",
            "--max-rounds", "2"
        ], catch_exceptions=False)

        assert result.exit_code == 0
        assert "Discussion Ended" in result.stdout

        # --- Assertions for Moderator.moderate call ---
        # The moderator is called once, before the agent in Round 2
        mock_moderator_moderate.assert_called_once()
        moderator_call_args = mock_moderator_moderate.call_args
        # The `full_history` is the second argument passed to `moderate`
        moderator_history_arg = moderator_call_args.args[1]

        expected_history_for_moderator = [
            {"role": "user", "content": topic, "name": "user"},
            {"role": "assistant", "content": mock_agent_response_r1.content, "name": "test-agent"}
        ]
        assert moderator_history_arg == expected_history_for_moderator

        # --- Assertions for Agent.generate_response calls ---
        assert mock_agent_generate_response.call_count == 2

        # First call (Round 1, Agent 1)
        agent_call_r1_args = mock_agent_generate_response.call_args_list[0]
        assert agent_call_r1_args.args[0] == topic # current_turn_prompt
        assert agent_call_r1_args.args[1] == [{"role": "user", "content": topic, "name": "user"}] # full_history

        # Second call (Round 2, Agent 1)
        agent_call_r2_args = mock_agent_generate_response.call_args_list[1]
        assert agent_call_r2_args.args[0] == mock_moderator_direction_r2 # current_turn_prompt
        expected_history_for_agent_r2 = expected_history_for_moderator + [{"role": "system", "content": mock_moderator_direction_r2, "name": mock_mod_agent.id}]
        assert agent_call_r2_args.args[1] == expected_history_for_agent_r2 # full_history