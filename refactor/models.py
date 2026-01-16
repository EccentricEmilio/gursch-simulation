import random
from state import GameState, Move, Card
from itertools import combinations
    
class RandomPolicy:
    def __str__(self):
        return "RandomPolicy"
    
    def return_move(self, state: GameState, player: str, moveset: set) -> Move:
        choice = random.choice(list(moveset))
        return choice

    def return_throw_amount(self, state: GameState, player: str) -> Move:
        throw_amount = random.randint(0,5)
        return throw_amount
    
    def return_throw(self, state: GameState, player: str, throw_amount: int) -> list[Card]:
        hand = state.players_hands[player]
        throw_combinations = combinations(hand, throw_amount)
        choice = random.choice(list(throw_combinations))
        return choice

class LeadWithHighestPolicy:
    def __init__(self):
        pass
    
class HumanPolicy:
    def print_hand(self, prefix: str, hand: list):
        message = [prefix]
        for card in hand:
            message.append(card)
        print(" ".join(message))
    
    def return_throw(self):
        return

    def return_move(self, state: GameState, player: str, moveset: set) -> Move:
        hand = state.players_hands[player]
    
        print("It's " + player + "'s turn.")
        self.print_hand("This is your hand:", hand)
        chosen_cards = input("Choose which cards to play: ")
        chosen_move = Move(chosen_cards.split())
        if chosen_move not in moveset:
            print("Invalid cards.")
            return self.return_move(state, player)
        print("You have played this move:", chosen_move)
        return chosen_move

