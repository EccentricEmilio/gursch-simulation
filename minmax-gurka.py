'''
Placeholder for minimax algorithm

function minimax(position, depth, maximizingPlayer)
	if depth == 0 or game over in position
		return static evaluation of position
 
	if maximizingPlayer
		maxEval = -infinity
		for each child of position
			eval = minimax(child, depth - 1, false)
			maxEval = max(maxEval, eval)
		return maxEval
 
	else
		minEval = +infinity
		for each child of position
			eval = minimax(child, depth - 1, true)
			minEval = min(minEval, eval)
		return minEval
 
 
// initial call
minimax(currentPosition, 3, true)

function minimax(position, depth, maximizingPlayer)
	if game over in position
		return static evaluation of position
 
	if maximizingPlayer
		maxEval = -infinity 
		for each child of position
            runningEval = []
            for i in 1000:
                determinize(child.enemyHand)
			    eval = minimax(child, depth - 1, false)
                runningEval.append(eval)
            averageEval = average(runningEval)

			maxEval = max(maxEval, averageEval)
		return maxEval
 
	else
		minEval = +infinity
		for each child of position
            runningEval = []
            for i in 1000:
                determinize(child.enemyHand)
                eval = minimax(child, depth - 1, true)
                runningEval.append(eval)
            averageEval = average(runningEval)
			minEval = min(minEval, eval)
		return minEval
 
 
// initial call
minimax(currentPosition, 3, true)
'''

'''
    Determinize needs to only create hands which are possible
    If a person has played card a against the value b
    where a <= b, then a = min(hand) and max(hand) <= b
    What a player knows about an opponents hand then changes every time the opponent plays a <= b
    in the beginning, the hand looks like this: 
    [(1 - 14), (1 - 14), (1 - 14)]

    If i play 12 and they in response plays 5, the hand changes:
    [5, (5 - 12), (5 - 12)]

    Generalized:
    If i play a and they in response plays b, the hand changes:
    [b, (b - a), (b - a)]

    We shall save a hand_info in State, that corresponds to what each player knows
    about the other player's hand. The first item in hand_info, hand_info[0]
    is then the publically attainable knowledge about player_0
'''

from statistics import mean
from random import shuffle
from dataclasses import dataclass
from copy import deepcopy

FULL_DECK = list(range(2, 15)) * 4
SIMULATIONS = 50
ALL_CARDS  = set(range(2, 15))
DEFAULT_HAND_INFO = [
    ALL_CARDS.copy(),
    ALL_CARDS.copy()
]
COUNT = 0

@dataclass
class State:
    hands: list
    hand_info: list
    current_player: int # index of hands
    highest_value: int # value to match, -1 means start of round
    round_winner: int  # Eventual round winner, -1 means start of round
    played_this_round: int # amount of cards that has been played this round
    played_cards: list # cards that have been played

    def __str__(self):
        return (
            f"hands={self.hands}\n"
            f"current_player={self.current_player}\n"
            f"highest_value={self.highest_value}\n"
            f"round_winner={self.round_winner}\n"
            f"played_this_round={self.played_this_round}\n"
            f"played_cards={self.played_cards}\n"
            f"hand_info={self.hand_info}"
        )

def is_terminal(state: State) -> bool:
    '''
    Check if the state is terminal
    Terminal means that the state is solved, every person knows what to play
    '''
    hand_lengths = [len(hand) for hand in state.hands]
    
    if 1 in hand_lengths:
        raise RuntimeError("Minimax went past a terminal state.")
    
    return all([(len==2) for len in hand_lengths])   

def get_terminal_eval(state: State) -> float:
    '''
    It takes in a state where every player has 2 cards.
    -1 means player 0 won (hands[0])
    0 means a draw 
    1 means player 1 won 
    '''
    if not state.played_this_round == 0:
        raise RuntimeError

    # Play first move
    state_copy = deepcopy(state)
    move = max(legal_moves(state_copy))
    state_copy = play_card(state_copy, move)

    # Every other player plays their highest card
    while not all([len(hand)==1 for hand in state_copy.hands]):
        state_copy = play_card(state_copy, max(legal_moves(state_copy)))

    # Check for draws
    flat_hands = [hand[0] for hand in state_copy.hands]
    max_value = max(flat_hands)

    if flat_hands[0] < max_value:
        # Player 0 won
        return 1.0
        
    elif flat_hands[1] < max_value:
        # Player 1 won
        return 0.0
    
    else:
        # Draw
        return 0.5

def legal_moves(state: State) -> list[int]:
    moves = []
    if state.played_this_round == 0:
        moves = deepcopy(state.hands[state.current_player])
    else:
        if max(state.hands[state.current_player]) > state.highest_value:
            moves = [c for c in state.hands[state.current_player] if c > state.highest_value]
        else:
            moves = [min(state.hands[state.current_player])]
    return moves


def play_card(state: State, move: int) -> State:
    '''
    Remove move from current_player's hand
    Update .value
    Increment .current_player and .played_this_round
    '''
    next_state = deepcopy(state)
    next_state.hands[next_state.current_player].remove(move)
    next_state.played_cards.append(move)

    if move > next_state.highest_value:
        # Update value and assign new eventual winner
        # Played above value
        next_state.highest_value = move
        next_state.round_winner = next_state.current_player
    else:
        # Played their smallest card
        # upper_ceiling calculates the minimum upper ceiling
        # just because i respond to a higher value, doesnt mean i can have the value-1
        # I must take into account what i remember from previous rounds
        upper_ceiling = min(next_state.highest_value, max(next_state.hand_info[next_state.current_player]))
        next_state.hand_info[next_state.current_player] = set(range(move, upper_ceiling+1))



    next_state.played_this_round += 1

    if next_state.played_this_round >= len(next_state.hands):
        # Last player has played
        # The person which played the highest value this round
        # shall be the new .current_player

        next_state.current_player = next_state.round_winner

        # Reset game for new round
        next_state.highest_value = -1
        next_state.round_winner = -1
        next_state.played_this_round = 0
    else:
        # Another player shall play

        # Increment .current_player
        if next_state.current_player >= (len(next_state.hands)-1):
            next_state.current_player = 0
        else:
            next_state.current_player += 1

    return next_state


def determinize(state: State, self_index: int) -> list[int]:
    '''
    '''
    if self_index == 0:
        enemy_index = 1
    else:
        enemy_index = 0

    hand_len = len(state.hands[enemy_index])

    unknown = list(state.hand_info[enemy_index]) * 4

    for card in state.hands[self_index] + state.played_cards:
        if card in unknown:
            unknown.remove(card)

    shuffle(unknown)
    return unknown[:hand_len]


def minimax(state: State) -> float:
    global COUNT
    #print(COUNT)
    COUNT += 1
    if is_terminal(state):
        return get_terminal_eval(state)

    if state.current_player == 0:
        # Maximizing player
        max_Eval = -100

        # Here we create len(legal_moves(state)) amount of child nodes
        # The parent node is state
        for card in legal_moves(state):
            running_eval = []
            child_state = play_card(state, card)
            # Here we determinize and calculate average for the node
            for _ in range(SIMULATIONS):
                determinized_state = deepcopy(child_state)
                determinized_state.hands[1] = determinize(
                    determinized_state,
                    0
                )
                eval = minimax(determinized_state)
                running_eval.append(eval)
            mean_eval = mean(running_eval)
            print(mean_eval)
            max_Eval = max(max_Eval, mean_eval)
        return max_Eval

    else:
        # Minimizing 
        min_Eval = 100
        for card in legal_moves(state):
            running_eval = []
            child_state = play_card(state, card)
            # Here we determinize and calculate average for the card
            for _ in range(SIMULATIONS):
                determinized_state = deepcopy(child_state)
                determinized_state.hands[0] = determinize(
                    determinized_state,
                    1
                )
                eval = minimax(determinized_state)
                running_eval.append(eval)
            mean_eval = mean(running_eval)
            print(mean_eval)
            min_Eval = min(min_Eval, mean_eval)
        return min_Eval
            


def choose_move(state: State):
    '''
    Assumes current_player == 0
    and hands is formatted like this:
    hands=[
        [int, int, int],
        [-1, -1, -1]
    ]
    '''
    
    moves = legal_moves(state)
    scores = {
        move: 0
        for move in moves
    }

    count = 0

    for move in scores:
        running_eval = []
        child_state = play_card(state, move)
        for i in range(SIMULATIONS):
            count += 1
            print(count)
            determinized_state = deepcopy(child_state)
            determinized_state.hands[1] = determinize(
                child_state.hands[0], 
                child_state.played_cards,
                len(child_state.hands[1])
            )
            eval = minimax(determinized_state, False)
            running_eval.append(eval)
        mean_eval = mean(running_eval)
        print(mean_eval)
        scores[move] += mean_eval
    return scores

def return_random_hand(len=3):
    shuffle(FULL_DECK)
    return FULL_DECK[:len]

state = State(
    hands=[
        [14, 14, 2],
        [-1, -1, -1]
    ],
    hand_info=DEFAULT_HAND_INFO,
    current_player=0,
    highest_value=-1,
    round_winner=-1,
    played_this_round=0,
    played_cards=[]
)

#scores = choose_move(state)
#print(scores)
eval = minimax(state)
print("finished", eval)
print(state)
