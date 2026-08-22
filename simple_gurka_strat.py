# For each possible hand, calculate every possible hand the enemy could have and what they would play if they had that hand against the card u played.
# A two card hand always plays the highest card possible.
# A player with a three card hand should look forward and calculate the move with the highest possibility of winning based on this



# When a winning player shall choose between two cards to play when starting the round, 
# it should choose the card that has the highest probability of winning.
# That card is always the highest card. [Prediction]

#TODO
#generate_theoretical hand only works on hand_size 4 or under because of .remove()


import random

from dataclasses import dataclass

from copy import deepcopy

HAND_SIZE = 2
A = "A"
B = "B"


class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []

    def draw_cards(self, cards):
        self.hand.extend(cards)

    def play_card(self, card):
        self.hand.remove(card)
        return card







def generate_deck():
    deck = list(range(1,15)) * 4
    #random.shuffle(deck)
    return deck

def deal_players(players):
    deck = generate_deck()
    for player in players:
        print(deck)
        cards = deck[0:HAND_SIZE]
        player.draw_cards(cards)
        del deck[0:HAND_SIZE]

def generate_theoretical_hand(self_hand):
    deck = generate_deck()
    for card in self_hand:
        deck.remove(card)
    random_hand = random.sample(deck, HAND_SIZE)
    return random_hand

def simulate_game(hand):
    arbitrary_enemy_hand = generate_theoretical_hand(hand)
    for card in hand:
        print(f"Played {card}")
        if card >= max(arbitrary_enemy_hand):
            # If B doesn't have any cards over played card
            arbitrary_enemy_hand.remove(min(arbitrary_enemy_hand))
        else:
            exit
            
        


def main():
    hand = [5, 10, 11]
    simulate_game(hand)
    

if __name__ == "__main__":
   # main()
   exit






'''
A has three cards, [A1], [A2], [A3]
A plays a card, [A1]
B must respond to [A1], we will use monte carlo to calculate best response for hand B
B generates random hand and imagines that A has it, it now has [A2] and [A3], which we know
B imagines playing [B1] in response to [A1]
Here there are two branching possibilities: 
    If [B1] >= [A1], B wins the round and goes on to play another card
    B then simply selects the highest card between [B2] and [B3]
    A responds with their highest legal card
    The person with the lowest card left wins

    If [B1] < [A1], A wins the round and A goes on to play another card
    A then simply selects the lowest card between [A2] and [A3]
    B responds with their highest legal card
    The person with the lowest card left wins

Regardless of what happens, B now assigns the card [B1] with +1 point if they won,
and +0 point if they lost, a draw would be a value between these, such as +0.5

B then continues with this N times, until they are satisfied with N
B then does this repeated for [B2] and [B3]
The card with the highest point score is the optimal card to play
'''
def return_legal_moves(value, hand):
    if max(hand) > value:
        legal_moves = [c for c in hand if c > value]
    else:
        legal_moves = [min(hand)]
    return legal_moves
'''
B = [5, 10, 11]
#a1 = random.randint(1,14)
a1 = 8
games = []
current_game = []
legal_B = return_legal_moves(a1, B)
point_list = [[key, 0.0] for key in legal_B]  
all_cards = B + [a1]    




count = 0

while count < 10000:
    A = generate_theoretical_hand(all_cards)



    for pair in point_list:
        current_game.append(A)
        b1 = pair[0]
        new_B = B.copy()
        new_B.remove(b1)

        current_game.append([(a1, "A"), (b1, "B")])
        if b1 > a1:
            # B won
            b2 = max(new_B)
            new_B.remove(b2) 

            legal_A = return_legal_moves(b2, A)

            new_A = A.copy()
            a2 = max(legal_A)
            new_A.remove(a2)

            current_game.append([(b2, "B"), (a2, "A")])


            b3 = new_B[0]
            a3 = new_A[0]


            current_game.append([(a3, "A"), (b3, "B")])

        else:
            # A won
            a2 = max(A)

            legal_B = return_legal_moves(a2, new_B)
            b2 = max(legal_B)

            current_game.append([(a2, "A"), (b2, "B")])

            new_A = A.copy()
            new_A.remove(a2)
            a3 = new_A[0]
            new_B.remove(b2)
            b3 = new_B[0]

            current_game.append([(a3, "A"), (b3, "B")])

        if a3 > b3:
            pair[1] += 1 
        elif a3 == b3:
            pair[1] += 0.5

        games.append(current_game)
        current_game = []
    count += 1
index = list(range(len(games)))
for i, game in zip(index, games):
    print(f"Game Number {i+1}")
    print(f"A hand: {game[0]}")
    print(f"A played: {a1}")
    moves = game.copy()
    del moves[0]
    print(moves)
print(point_list)
'''

@dataclass
class State:
    hands: list
    current_player: int # index of hands
    value: int # value to match
    round_winner: int | None # not currently used
    played_this_round: int 
    # amount of cards that has been played this round

'''
hands = [
    [], -root_player
    [], 
    [],
]
index shows which player it is
'''



FULL_DECK = list(range(1, 14)) * 4

def terminal(state) -> bool:
    # Return 1 if all hands are only 1 card and state.played == 0
    return (
        all([(len(hand) == 1) for hand in state.hands]) 
        and state.played == 0
    )    

def final_round_result(state) -> float:
    '''
    This function always returns the final_result based on
    the root_player's perspective.
    '''
    flat_hands = []
    for hand in state.hands:
        for card in hand:
            flat_hands.append(card)
    max_value = max(flat_hands)
    if max_value.count() > 1:
        # Draw
        if flat_hands[0] == max_value:
            # player was in draw
            result = 0.5 
        else:
            # player won
            result = 1.0
    else:
        if flat_hands[0] == max_value:
            result =  0.0
        else:
            result = 1.0

    return result


def legal_moves(state) -> list[int]:
    moves = []
    if state.played_this_round == 0:
        for card in state.hands[state.current_player]:
            moves.append(card)
        return moves
    else:
        if max(state.hands[state.current_player]) > state.value:
            moves = [c for c in state.hand if c > state.value]
        else:
            moves = [min(state.hands[state.current_player])]
    return moves


def play_card(state: State, move: int) -> State:
    next_state = deepcopy(state)

    
    next_state.hands[state.current_player].remove(move)

    if next_state.current_player >= (len(next_state.hands)-1):
        next_state.current_player = 0
        next_state.played_this_round = 0
    else:
        next_state.current_player += 1
        next_state.played_this_round += 1

    return next_state
    
def determinize(my_hand, known_cards, num_players):

    unknown = FULL_DECK.copy()

    for card in my_hand + known_cards:
        unknown.remove(card)

    random.shuffle(unknown)

    hands = [my_hand[:]]

    cards_per_opponent = len(my_hand)

    index = 0

    for _ in range(num_players - 1):
        hand = unknown[index:index + cards_per_opponent]
        hands.append(hand)
        index += cards_per_opponent

    return hands


def minimax(state, root_player) -> float |  list:

    if terminal(state):
        result = final_round_result(state)
        return result 
    

    moves = legal_moves(state)

    results = []

    for move in moves:
        next_state = play_card(state, move)

        value = minimax(next_state, root_player)

        results.append(value)

    if state.current_player == root_player:
        return max(results)
    else:
        return min(results)




def choose_move(my_hand, known_cards, game_state, num_players):

    moves = set(legal_moves(game_state))
    # set() to remove duplicates,
    # since it doesnt matter which duplicate you choose

    scores = {
        move: 0
        for move in moves
    }
    print(scores)

    simulations = 10000

    for _ in range(simulations):

        hands = determinize(
            my_hand,
            known_cards,
            num_players
        )

        state = State(
            hands=hands,
            current_player=game_state.current_player,
            value=game_state.value,
            round_winner=game_state.round_winner,
            played_this_round=game_state.played_this_round
        )

        for move in moves:

            next_state = play_card(state, move)

            value = minimax(
                next_state,
                root_player=0
            )

            scores[move] += value

    return max(
        scores,
        key=scores.get
    )






state = State(
    hands=[
        [4, 7, 12],
        [2, 9, 13]
    ],
    current_player=0,
    value=0,
    round_winner=None,
    played_this_round=0,
)

moves = legal_moves(state)

scores = {
    move: 0
    for move in moves
}
print(scores)