import random 
from .state import ObservableState, state_from_observable
from . import minmax
from . import mcts

class Agent:
    def get_action(self, observable_state: ObservableState, legal_actions: list[tuple[int, ...]]) -> tuple[int, ...]:
        raise NotImplementedError("This method should be implemented by subclasses.")


class HighestCardAgent(Agent): 
    def get_action(self, observable_state: ObservableState, legal_actions: list[tuple[int, ...]]) -> tuple[int, ...]:
        return max(legal_actions, key=lambda m: (max(m), len(m)))


class RandomAgent(Agent):
    def get_action(self, observable_state: ObservableState, legal_actions: list[tuple[int, ...]]) -> tuple[int, ...]:
        return random.choice(legal_actions)


class MaxNAgent(Agent):
    def __init__(self, simulations: int = 100):
        self.simulations = simulations

    def get_action(self, observable_state: ObservableState, legal_actions: list[tuple[int, ...]]) -> tuple[int, ...]:
        obs_state = state_from_observable(observable_state)
        move_values = minmax.choose_move_maxn(obs_state, simulations=self.simulations)

        chosen_move = max(move_values, key=lambda k: move_values[k])
        return chosen_move


class MCTSAgent(Agent):
    def __init__(self, iterations: int = 1000, c: float = 0.7):
        self.iterations = iterations
        self.c = c

    def get_action(self, observable_state: ObservableState, legal_actions: list[tuple[int, ...]]) -> tuple[int, ...]:
        obs_state = state_from_observable(observable_state)
        move_values = mcts.choose_move_mcts(obs_state, iterations=self.iterations, c=self.c)

        chosen_move = max(move_values, key=lambda k: move_values[k])
        return chosen_move


class MixedMaxNMCTS(Agent):
    def __init__(self, maxN_iterations: int = 100, mcts_iterations: int = 1000, c: float = 0.7, size_limit: int = 5):
        self.maxN_iterations = maxN_iterations
        self.mcts_iterations = mcts_iterations
        self.c = c
        self.size_limit = size_limit

    def get_action(self, observable_state: ObservableState, legal_actions: list[tuple[int, ...]]) -> tuple[int, ...]:
        state = state_from_observable(observable_state)

        if len(observable_state.own_hand) <= self.size_limit:
            # Use MaxN
            move_values = minmax.choose_move_maxn(state, simulations=self.maxN_iterations)
            chosen_move = max(move_values, key=lambda k: move_values[k])
        else: 
            # Use MCTS
            move_values = mcts.choose_move_mcts(state, iterations=self.mcts_iterations, c=self.c)
            chosen_move = max(move_values, key=lambda k: move_values[k])
        return chosen_move


# TODO
class HumanAgent(Agent):
    def get_action(self, observable_state: ObservableState, legal_actions: list[tuple[int, ...]]) -> tuple[int, ...]:
        print("Your turn!")
        print(f"Your hand: {observable_state.own_hand}")
        print("Enemy info:")
        for index, info in enumerate(list(observable_state.hand_info)):
            if index != observable_state.viewer:

                print(f"Player {index}: {min(info)} - {max(info)} are possible values")
        print(f"Legal actions: {legal_actions}")
        while True:
            try:
                action = int(input("Enter your action: "))
                if action in legal_actions:
                    return action
                else:
                    print(f"Invalid action. Please choose from {legal_actions}.")
            except ValueError:
                print("Invalid input. Please enter a number.")