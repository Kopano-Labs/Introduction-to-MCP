import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from orch.orchestration import ORCHApprentice
from orch import logging


class DummyMentor:
    def __init__(self, name):
        self.name = name

    def respond(self, prompt):
        return f"{self.name} says: {prompt.upper()}"


def test_orch_logging(tmp_path, monkeypatch):
    monkeypatch.setattr(logging, "AUDIT_DIR", tmp_path)
    tmp_path.mkdir(exist_ok=True)

    orch = ORCHApprentice([DummyMentor("Claude"), DummyMentor("Gemini")])
    result = orch.learn("hello")

    assert "CLAUDE" in result.upper()
    assert "GEMINI" in result.upper()

    # Check logs
    reasoning_file = tmp_path / "reasoning.jsonl"
    execution_file = tmp_path / "execution.jsonl"

    assert reasoning_file.exists()
    assert execution_file.exists()
    assert "Received prompt" in reasoning_file.read_text()
    assert "mentor:Claude" in execution_file.read_text()
