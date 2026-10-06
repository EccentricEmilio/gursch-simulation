import sys
from pathlib import Path

# Add the repository root to Python's import path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from gursh import engine as gu_engine, state as gu_state

def test_get_utilities():
    played_moves = [
        [9, 9],
        [10, 11],
        [2, 7],
    ]
    state = gu_state.create_new_state(hands=[[], [], []], player_count=3, played_moves=played_moves)
    print(state)
    utils = gu_engine.get_utilities(state)
    print(utils)
    assert len(utils) == len(state.hands), "length should be same as amount of players"
    assert sum(utils) == 0, "sum should be 0"

if __name__ == "__main__":
    test_get_utilities()