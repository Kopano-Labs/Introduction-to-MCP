"""
Test Suite for Simulator Round-Robin Logic
Architect: www.linkedin.com/in/kholofelo-robyn-rababalela-7a26273b7
GitHub: https://github.com/RobynAwesome/
"""
import pytest
from orch.simulator import run_simulation

class MockAgent:
    def __init__(self, id, model):
        self.id = id
        self.model = model

class MockModerator:
    def __init__(self):
        self.called = 0
    def moderate(self, topic, history):
        self.called += 1
        return "Mock Prompt"

def test_round_robin_execution_order(mocker):
    """Validates that agents are called in a strict round-robin sequence."""
    mocker.patch('orch.simulator.completion', return_value=mocker.Mock(choices=[mocker.Mock(message=mocker.Mock(content="Mock Response"))]))
    mocker.patch('orch.datalake.start_discussion', return_value=1)
    mocker.patch('orch.datalake.log_interaction')
    
    agents = [MockAgent("agent1", "model1"), MockAgent("agent2", "model2")]
    moderator = MockModerator()
    
    history = run_simulation(
        topic="Test Topic",
        agents=agents,
        moderator=moderator,
        max_rounds=2
    )
    
    # 2 rounds * 2 agents = 4 messages generated
    assert len(history) == 4
    assert history[0]["name"] == "agent1"
    assert history[1]["name"] == "agent2"