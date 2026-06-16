
import sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "kopano-core"))

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from kopano.simulator import run_simulation, _handle_tool_calls

@pytest.mark.asyncio
async def test_handle_tool_calls():
    # Mocking execute_tool_code to avoid side effects
    with patch("kopano.simulator.execute_tool_code") as mock_execute, \
         patch("kopano.simulator._broadcast") as mock_broadcast, \
         patch("kopano.simulator.log_interaction") as mock_log:
        
        mock_execute.return_value = "File content"
        reply = "I will read the file. <tool_code>read_file(\"test.txt\")</tool_code>"
        
        result = await _handle_tool_calls(reply, "agent1", 1, 1)
        
        assert "File content" in result
        mock_execute.assert_called_once_with("read_file(\"test.txt\")")
        assert mock_broadcast.call_count == 2 # tool_execution and tool_result
        mock_log.assert_called_once()

@pytest.mark.asyncio
async def test_run_simulation_basic():
    # Mocking agents and moderator
    agent = MagicMock()
    agent.id = "agent1"
    agent.model = "gpt-4"
    agent.agenerate_response = AsyncMock(return_value=MagicMock(content="Hello"))
    
    moderator = MagicMock()
    moderator.agent = MagicMock(id="mod1", model="gpt-4")
    moderator.amoderate = AsyncMock(return_value="Continue")
    
    with patch("kopano.simulator._broadcast") as mock_broadcast, \
         patch("kopano.simulator.log_interaction") as mock_log_interaction, \
         patch("kopano.simulator.log_message") as mock_log_message, \
         patch("kopano.simulator.get_db_connection") as mock_db, \
         patch("kopano.simulator.bridge") as mock_bridge:
        
        # Mock DB cursor
        mock_cursor = MagicMock()
        mock_db.return_value.cursor.return_value = mock_cursor
        mock_cursor.lastrowid = 1
        
        mock_bridge.is_configured.return_value = False
        
        history = await run_simulation(
            topic="Test Topic",
            agents=[agent],
            moderator=moderator,
            max_rounds=1
        )
        
        assert len(history) == 1
        assert history[0]["content"] == "Hello"
        agent.agenerate_response.assert_called_once()
        moderator.amoderate.assert_not_called()
        assert mock_broadcast.called
        assert mock_log_interaction.called
        assert mock_log_message.called
