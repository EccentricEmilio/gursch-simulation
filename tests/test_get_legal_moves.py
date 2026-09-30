import sys
from pathlib import Path

# Add the repository root to Python's import path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from gursh import engine as gu_engine, state as gu_state

def test_get_legal_moves_lead():
    state = gu_state.create_new_state(player_count=4, hand_size=4)
    legal_moves = gu_engine.get_legal_moves(state)
    print("Hand: ", state.hands[state.current_player])
    print("Legal moves for lead:", legal_moves)
    assert all(isinstance(move, list) for move in legal_moves), "All moves should be lists"
    assert all(len(move) > 0 for move in legal_moves), "All moves should have at least one card"
    assert all(all(isinstance(card, int) for card in move) for move in legal_moves), "All cards should be integers"
    

test_get_legal_moves_lead()