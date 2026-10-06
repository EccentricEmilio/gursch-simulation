import sys
from pathlib import Path

# Add the repository root to Python's import path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from gursh import engine as gu_engine, state as gu_state, agents as gu_agents

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


def test_random_state():
    agents: list[gu_agents.RandomAgent] = [gu_agents.RandomAgent()] * 3

    state = gu_state.create_new_state(player_count=len(agents), hand_size=5)
    print("Hands: ", state.hands)

    while not state.is_game_over():
        current_player = state.current_player

        obs = state.get_observable_state(current_player)

        legal_actions = gu_engine.get_legal_moves(state)
        action = agents[current_player].get_action(obs, legal_actions)
        if not action in legal_actions:
            raise ValueError(f"Illegal action {action} for player {current_player}. Legal actions: {legal_actions}")
        print(f"Player {current_player} plays {action}")
        state = gu_engine.apply_action(state, action)

    print("State", state)

    utils =  gu_engine.get_utilities(state)
    print(utils)
    assert state.is_game_over() == True, "game should be over"
    assert len(utils) == len(state.hands), "length should be same as amount of players"
    assert sum(utils) == 0, "sum should be 0"


if __name__ == "__main__":
    test_random_state()