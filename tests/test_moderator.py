"""
Pytest tests for the Phase 2 Moderator AI logic.
"""
import pytest
from unittest.mock import patch, MagicMock

from orch.orch.moderator import Moderator
from orch.orch.agent_manager import Agent

@patch('orch.orch.moderator.load_agents')
def test_moderator_initialization_success(mock_load_agents):
    """
    Test that the Moderator initializes correctly with a valid agent.
    """
    mock_agent = Agent(id="gpt-4o-mod", provider="openai", model="gpt-4o", api_key="fake-key", persona="")
    mock_load_agents.return_value = {"gpt-4o-mod": mock_agent}
    
    moderator = Moderator(agent_id="gpt-4o-mod")
    assert moderator.agent.id == "gpt-4o-mod"

@patch('orch.orch.moderator.load_agents')
def test_moderator_initialization_fail(mock_load_agents):
    """
    Test that the Moderator raises an error if the agent is not found.
    """
    mock_load_agents.return_value = {}
    with pytest.raises(ValueError, match="Moderator agent 'gpt-4o-mod' not found."):
        Moderator(agent_id="gpt-4o-mod")

@patch('orch.orch.moderator.completion')
@patch('orch.orch.moderator.load_agents')
def test_moderator_moderate_success(mock_load_agents, mock_completion):
    """
    Test the moderate method successfully returns a new direction from the LLM.
    """
    # Setup mock agent
    mock_agent = Agent(id="gpt-4o-mod", provider="openai", model="gpt-4o", api_key="fake-key", persona="")
    mock_load_agents.return_value = {"gpt-4o-mod": mock_agent}

    # Setup mock litellm completion response
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "What is the next logical step?"
    mock_completion.return_value = mock_response

    # Initialize moderator and run test
    moderator = Moderator(agent_id="gpt-4o-mod")
    history = [{"name": "gemini", "content": "I think A is the answer."}]
    topic = "Test Topic"
    
    direction = moderator.moderate(topic, history)

    assert direction == "What is the next logical step?"
    mock_completion.assert_called_once()
    call_args = mock_completion.call_args
    assert call_args.kwargs['model'] == "gpt-4o"
    assert "Test Topic" in call_args.kwargs['messages'][1]['content']
    assert "[gemini]: I think A is the answer." in call_args.kwargs['messages'][1]['content']

@patch('orch.orch.moderator.completion')
@patch('orch.orch.moderator.load_agents')
def test_moderator_moderate_api_failure(mock_load_agents, mock_completion):
    """
    Test the moderate method falls back gracefully when the API call fails.
    """
    # Setup mock agent
    mock_agent = Agent(id="gpt-4o-mod", provider="openai", model="gpt-4o", api_key="fake-key", persona="")
    mock_load_agents.return_value = {"gpt-4o-mod": mock_agent}

    # Setup mock litellm to raise an exception
    mock_completion.side_effect = Exception("API Error")

    # Initialize moderator and run test
    moderator = Moderator(agent_id="gpt-4o-mod")
    history = []
    topic = "Failing Topic"
    
    direction = moderator.moderate(topic, history)

    assert direction == "Please continue the discussion on Failing Topic."