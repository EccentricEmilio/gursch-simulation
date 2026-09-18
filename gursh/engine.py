from copy import deepcopy

def get_legal_actions(state) -> list[int]:
    moves = []
    current_player_hand = list(set(state.hands[state.current_player])) 
    if state.played_this_round == 0:
        moves = current_player_hand
    else:
        if max(current_player_hand) > state.highest_value:
            moves = [c for c in current_player_hand if c > state.highest_value]
        else:
            moves = [min(current_player_hand)]
    return moves

def apply_action(state, move: int):
    '''
    Remove move from current_player's hand
    Update .value
    Increment .current_player and .played_this_round
    '''
    next_state = deepcopy(state)
    next_state.hands[next_state.current_player].remove(move)
    next_state.played_cards.append(move)

    if (next_state.highest_value is None) or (move > next_state.highest_value):
        # Update value and assign new eventual winner
        # Played above value
        next_state.highest_value = move
        next_state.round_leader = next_state.current_player
    else:
        # Played their smallest card and is not the first round
        # upper_ceiling calculates the minimum upper ceiling

        # just because i respond to a higher value, doesnt mean i can have the value-1
        # I must take into account what i remember from previous rounds
        upper_ceiling = min(next_state.highest_value, max(next_state.hand_info[next_state.current_player]))
        next_state.hand_info[next_state.current_player] = set(range(move, upper_ceiling+1))

    next_state.played_this_round += 1

    if next_state.played_this_round == len(next_state.hands):
        # Last player has played
        # The person which played the highest value this round
        # shall be the new .current_player

        next_state.current_player = next_state.round_leader

        # Reset game for new round
        next_state.highest_value = None
        next_state.round_leader = None
        next_state.played_this_round = 0
    else:
        # Another player shall play

        # Increment .current_player
        next_state.current_player = (next_state.current_player + 1) % len(next_state.hands)

    return next_state