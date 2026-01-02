import random
from state import GameState

# Chat told me to use this, cant see why though?
class Move:
    def __init__(self):
        pass

class RandomPolicy:
    def __init__(self):
        pass
    
    def return_move(self, state: GameState, player, legal_moves):
        # Can only choose one card?
        return random.choice(legal_moves)

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
    
    def print_starting_player(self, player: str):
        print("The starting player is:", player)
    
    def print_loser(self, loser_score: tuple, ties):
        if ties == []:
            loser = loser_score[0]
            score = loser_score[1]
            print("Game is over")
            print(loser + " lost, with a score of " + str(score))
        elif ties != []:
            print("It's a tie!")
            print("These players tied: " + str(ties))