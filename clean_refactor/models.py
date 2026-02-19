import random
from state import GameState, Move, Card
from itertools import combinations

class RandomPolicy:
    def __str__(self):
        return "RandomPolicy"

    def return_move(self, state: GameState, player: str, moveset: set) -> Move:
        choice = random.choice(list(moveset))
        return choice

    def return_throw_amount(self, state: GameState, player: str) -> int:
        throw_amount = random.randint(0,5)
        return throw_amount

    def return_throw(self, state: GameState, player: str, throw_amount: int) -> list[Card]:
        hand = state.players_hands[player]
        throw_combinations = combinations(hand, throw_amount)
        choice = random.choice(list(throw_combinations))
        return list(choice)


class HighestPolicy:
    def __init__(self):
        self.DISLIKED_VALUES = [8, 9, 10, 11, 12]
        self.VALUES_RANKED = [7, 14, 2, 13, 3, 4, 5, 6, 12, 11, 10, 9, 8]

    def __str__(self):
        return "HighestPolicy"

    def return_move(self, state: GameState, player: str, moveset: set) -> Move:
        highest_move = max(
            moveset,
            key=lambda m: (len(m), m.return_true_score())
        )
        return highest_move

    def return_throw_amount(self, state: GameState, player: str) -> int:
        hand_values = [c.int_value for c in state.players_hands[player]]
        disliked_values = [val for val in hand_values if val in self.DISLIKED_VALUES]
        throw_amount = len(disliked_values)
        return throw_amount

    def return_throw(self, state: GameState, player: str, throw_amount: int) -> list[Card]:
        hand = state.players_hands[player]
        sorted_hand = sorted(hand,
                             key=lambda m: self.VALUES_RANKED.index(m.int_value),
                             reverse=True)
        choice = sorted_hand[:throw_amount]
        return choice
