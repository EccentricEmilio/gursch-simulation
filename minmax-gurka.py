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
	if depth == 0 or game over in position
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
Player 0 is maximizing
'''

from statistics import mean
from random import shuffle
from dataclasses import dataclass
from copy import deepcopy

FULL_DECK = list(range(1, 15)) * 4
SIMULATIONS = 100

@dataclass
class State:
    hands: list
    current_player: int # index of hands
    highest_value: int # value to match, -1 means start of round
    round_winner: int  # Eventual round winner, -1 means start of round
    played_this_round: int # amount of cards that has been played this round
    played_cards: list # cards that have been played


def is_terminal(state: State) -> bool:
    '''
    Return 1 if all hands are only 1 card and state.played == 0
    '''
    return (
        all([(len(hand) == 1) for hand in state.hands]) 
        and state.played_this_round == 0
    )    


def is_evaluable(state: State) -> bool:
    '''
    If the game has people with only 2 cards in their hands, we can say that the game is solved
    since every person knows what card to play.
    '''
    if all([len(hand)==2 for hand in state.hands]):
        return True
    else:
        return False


def simulate_evaluable_game(state: State) -> int:
    '''
    It takes in a state where every player has 2 cards.
    This function returns a int
    -1 means player 0 won (hands[0])
    0 means a draw 
    1 means player 1 won 
    '''
    end_state = deepcopy(state)

    move = max(end_state.hands[end_state.current_player])
    end_state = play_card(end_state, move)

    while not is_terminal(end_state):
        moves = legal_moves(end_state)
        end_state = play_card(end_state, max(moves))

    # Check for draws
    flat_hands = [hand[0] for hand in end_state.hands]

    max_value = max(flat_hands)

    if flat_hands[0] < max_value:
        # Player 0 won
        return -1
        
    elif flat_hands[1] < max_value:
        # Player 1 won
        return 1
    
    else:
        # Draw
        return 0


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
        next_state.highest_value = move
        next_state.round_winner = next_state.current_player


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


def determinize(own_hand: list, known_cards: list, length) -> list[int]:
    '''
    Determinized_index is the index of which hand to determinize
    '''

    unknown = FULL_DECK.copy()

    for card in own_hand:
        unknown.remove(card)


    for card in known_cards:
        unknown.remove(card)

    shuffle(unknown)
    return unknown[:length]
    


def minimax(state: State, maximizing_player: bool) -> int:
    if is_evaluable(state):
        return simulate_evaluable_game(state)

    if maximizing_player:
        max_Eval = -100
        for card in state.hands[0]:
            running_eval = []
            child_state = play_card(state, card)
            # Here we determinize and calculate average for the card
            for i in range(SIMULATIONS):
                determinized_state = deepcopy(child_state)
                determinized_state.hands[1] = determinize(
                    child_state.hands[0], 
                    child_state.played_cards,
                    len(child_state.hands[1])
                )
                eval = minimax(determinized_state, False)
                running_eval.append(eval)
            mean_eval = mean(running_eval)
            max_Eval = max(max_Eval, mean_eval)
        return max_Eval

    else:
        min_Eval = 100
        for card in state.hands[1]:
            running_eval = []
            child_state = play_card(state, card)

            for i in range(SIMULATIONS):
                determinized_state = deepcopy(child_state)
                determinized_state.hands[0] = determinize(
                    child_state.hands[1], 
                    child_state.played_cards,
                    len(child_state.hands[0])
                )
                eval = minimax(child_state, True)
                running_eval.append(eval)
            mean_eval = mean(running_eval)
            min_Eval = min(min_Eval, mean_eval)
        return min_Eval
            


def choose_move(my_hand, known_cards, game_state: State, num_players):

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
            highest_value=game_state.highest_value,
            round_winner=game_state.round_winner,
            played_this_round=game_state.played_this_round,
            played_cards=game_state.played_cards
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
        [2, 14, 14],
        [-1, -1, -1]
    ],
    current_player=0,
    highest_value=-1,
    round_winner=-1,
    played_this_round=0,
    played_cards=[]
)

eval = minimax(state, True)
print(eval)