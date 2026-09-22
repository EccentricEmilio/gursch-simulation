import random 
from .state import ObservableState, state_from_observable
from . import minmax

class Agent:
    def get_action(self, observable_state: ObservableState, legal_actions: list[int]) -> int:
        raise NotImplementedError("This method should be implemented by subclasses.")


class HighestCardAgent(Agent): 
    def get_action(self, observable_state: ObservableState, legal_actions: list[int]) -> int:
        return max(legal_actions)


class RandomAgent(Agent):
    def get_action(self, observable_state: ObservableState, legal_actions: list[int]) -> int:
        return random.choice(legal_actions)


class MaxNAgent(Agent):
    def __init__(self, simulations: int = 100):
        self.simulations = simulations

    def get_action(self, observable_state: ObservableState, legal_actions: list[int]) -> int:
    
        state = state_from_observable(observable_state)

        move_values = minmax.choose_move_maxn(state, simulations=self.simulations)

        chosen_move = max(move_values, key=lambda k: move_values[k])
        return chosen_move


class HumanAgent(Agent):
    def get_action(self, observable_state: ObservableState, legal_actions: list[int]) -> int:
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