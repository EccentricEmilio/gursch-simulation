import random 
from gursh.state import State, ObservableState as ObsState

class RandomAgent:
    def __init__(self):
        pass

    def get_action(self, observable_state: ObsState, legal_actions: list[int]) -> int:
        return random.choice(legal_actions)


class MaxNAgent:
    def __init__(self, simulations: int = 100):
        self.simulations = simulations

    def get_action(self, observable_state: ObsState, legal_actions: list[int]) -> int:
        from gursh.minmax import choose_move_maxn

        state = observable_state

        move_values = choose_move_maxn(state, simulations=self.simulations)

        chosen_move = max(move_values, key=lambda k: move_values[k])
        return chosen_move