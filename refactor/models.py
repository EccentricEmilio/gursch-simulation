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

class HighestPolicy:
    def __init__(self):
        self.DISLIKED_VALUES = [8, 9, 10, 11, 12]
        self.VALUES_RANKED = [7, 14, 2, 13, 3, 4, 5, 6, 12, 11, 10, 9, 8]
    
    
    def __str__(self):
        return "HighestPolicy"
    
    def return_move(self, state: GameState, player: str, moveset: set) -> Move: 
        #cur_round = state.current_round
        #if cur_round.starting_player == player:
            #pass
        #else:
            #pass
            #lead_move = cur_round.turns[0].move 
        
        highest_move = max(
            moveset,
            key=lambda m: (len(m), m.return_true_score())
        )

        return highest_move

    def return_throw_amount(self, state: GameState, player: str) -> Move:
        hand_values = [c.int_value for c in state.players_hands[player]]
        throw_amount = 0
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


class AiPolicy:
    def __init__(self):
        pass
    
    def return_move(self):
        #ai stuff
        pass




player = {
    "Abraham": [
        Move([Card("7", "H"), 
             Card("7","S"), 
             Card("7","S"), 
             Card("K","H"), 
             Card("K","C")]
        ),
        Move([Card("7", "H"), 
             Card("7","S"), 
             Card("7","S"), 
             Card("J","H"), 
             Card("J","C")] 
        )
        ]
    }
'''
move_1 = Move([Card("3", "H")])
move_2 = Move([Card("A", "S")])

move_3 = Move([Card("7", "H"), Card("7", "S")])
move_4 = Move([Card("K", "D"), Card("K", "C")])

move_5 = Move([Card("5", "H"), Card("5", "S"), Card("5", "D")])
move_6 = Move([Card("Q", "H"), Card("Q", "C"), Card("Q", "S")])

move_7 = Move([Card("9", "H"), Card("9", "S"), Card("9", "D"), Card("9", "C")])

move_11 = Move([
    Card("7", "H"), Card("7", "S"), Card("7", "D"),
    Card("K", "H"), Card("K", "C")
])

move_12 = Move([Card("A", "H"), Card("A", "S")])
move_13 = Move([Card("6", "H"), Card("6", "S"), Card("6", "D")])

moves = {
    move_1, move_2, move_3, move_4, move_5, move_6,
    move_7, move_11, move_12, move_13
}   


'''