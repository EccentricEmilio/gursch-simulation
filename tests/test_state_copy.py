import sys
from pathlib import Path

# Add the repository root to Python's import path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from gursh import state

def test_state_copy():
    error_msg = "state.copy() did not create a deep copy of the state"
    state_1 = state.create_new_state()
    state_2 = state_1.copy()
    state_2.hands[0][0] = 99
    assert state_1.hands[0][0] != 99, error_msg
    state_2.played_cards.append(99)
    assert 99 not in state_1.played_cards, error_msg
    state_2.hand_info[0].add(99)
    assert 99 not in state_1.hand_info[0], error_msg
    state_2.current_player = 1
    assert state_1.current_player != 1, error_msg
    state_2.highest_value = 99
    assert state_1.highest_value != 99, error_msg

test_state_copy()