import sys
from pathlib import Path

# Add the repository root to Python's import path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from gursh import state as gu_state, minmax as gu_minmax

def test_choose_move_maxn(player_count: int = 3, hand_size: int = 4, simulations: int = 100):
    state = gu_state.create_new_state(player_count=player_count, hand_size=hand_size)
    print(state)
    print(f"Acting player: {state.current_player}")
    values = gu_minmax.choose_move_maxn(state, simulations=simulations)
    print(f"Values (from acting player's perspective): {values}")
    best_move = max(values, key=lambda k: values[k])
    print(f"Best move: {best_move}")

if __name__ == "__main__":
    test_choose_move_maxn()