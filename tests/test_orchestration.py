
import sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "kopano-core"))

import pytest

# Example function to test (replace with your orchestration logic)
def add_numbers(a, b):
    return a + b

def test_add_numbers():
    result = add_numbers(2, 3)
    assert result == 5
