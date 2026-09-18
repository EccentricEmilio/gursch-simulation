import random 

class RandomAgent:
    def __init__(self):
        pass

    def get_action(self, observable_state, legal_actions: list[int]) -> int:
        return random.choice(legal_actions)