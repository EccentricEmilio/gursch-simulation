import random
from state import GameState, Move

class RandomPolicy:
    def __init__(self):
        pass

    def __str__(self):
        return "RandomPolicy"
    
    def return_move(self, state: GameState, player: str, moveset: set) -> Move:
        choice = random.choice(list(moveset))
        return choice

class LeadWithHighest:
    def __init__(self):
        pass
    
class HumanPolicy:
    def print_hand(self, prefix: str, hand: list):
        message = [prefix]
        for card in hand:
            message.append(card)
        print(" ".join(message))

    def prompt_player(self, player: str, hand: list, validate_player_input: callable):
            print("It's " + player + "'s turn.")
            self.print_hand("This is your hand:", hand)
            chosen_cards = input("Choose which cards to play: ")
            chosen_cards = chosen_cards.split()

            valid, err = validate_player_input(player, chosen_cards)
            if not valid:
                print(err)
                return self.prompt_player(player, hand, validate_player_input)

            self.print_hand("You have chosen these cards:", chosen_cards)
            return chosen_cards


POLICIES = [
    RandomPolicy(),
    RandomPolicy(),
    RandomPolicy()
]