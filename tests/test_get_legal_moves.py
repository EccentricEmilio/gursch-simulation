import sys
from pathlib import Path

# Add the repository root to Python's import path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from gursh import engine as gu_engine, state as gu_state, agents

def test_get_legal_moves_lead():
    print("Test_get_legal_moves_lead()")
    state = gu_state.create_new_state(player_count=4, hand_size=4)
    legal_moves = gu_engine.get_legal_moves(state)
    print("Hand: ", state.hands[state.current_player])
    print("Legal moves for lead:", legal_moves)
    assert all(isinstance(move, tuple) for move in legal_moves), "All moves should be tuples"
    assert all(len(move) > 0 for move in legal_moves), "All moves should have at least one card"
    assert all(all(isinstance(card, int) for card in move) for move in legal_moves), "All cards should be integers"


def test_get_legal_moves_response():
    print("Test_get_legal_moves_response()")
    state = gu_state.create_new_state(player_count=4, hand_size=4)
    random_agent = agents.RandomAgent()
    action = random_agent.get_action(
        state.get_observable_state(state.current_player), 
        gu_engine.get_legal_moves(state)
        )
    state = gu_engine.apply_action(state, action)

    legal_moves = gu_engine.get_legal_moves(state)

    print("Hand: ", state.hands[state.current_player])
    print("Lead Move: ", state.played_moves[0])
    print(f"Legal moves for response, player {state.current_player}:", legal_moves)
    assert all(isinstance(move, tuple) for move in legal_moves), "All moves should be tuples"
    assert all(len(move) > 0 for move in legal_moves), "All moves should have at least one card"
    assert all(all(isinstance(card, int) for card in move) for move in legal_moves), "All cards should be integers"


if __name__ == "__main__":
    test_get_legal_moves_lead()
    test_get_legal_moves_response()