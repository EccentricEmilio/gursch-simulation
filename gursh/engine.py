from copy import deepcopy
from collections import Counter
import random
from .state import State

def get_legal_actions(state: State) -> list[int]:
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

def apply_action(state: State, move: int) -> State:
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
        next_state.highest_value = -1
        next_state.round_leader = -1
        next_state.played_this_round = 0
    else:
        # Another player shall play

        # Increment .current_player
        next_state.current_player = (next_state.current_player + 1) % len(next_state.hands)

    return next_state


def determinize_state(state: State, self_index: int, max_attempts: int = 500) -> State:
    '''
    Sample a plausible joint assignment of hands for every player other than
    self_index, consistent with what self_index actually knows.

    This must be done jointly, not one opponent at a time: a card sampled
    into opponent A's hand is no longer available for opponent B, so
    determinizing opponents independently can (and will) double-allocate
    cards once there are 2+ hidden hands.

    Approach: build the true pool of unknown cards (full deck minus
    self_index's own hand and all played cards), then randomly assign each
    other player a hand of the right size drawn only from values their
    hand_info permits. This is a constrained bipartite assignment; a
    feasible solution always exists (the real hidden state is one), but a
    naive greedy pass can paint itself into a corner, so we retry with a
    fresh random order/shuffle on failure.
    '''
    other_indices = [i for i in range(len(state.hands)) if i != self_index]

    full_deck = Counter({rank: 4 for rank in range(2, 15)})
    known = Counter(state.hands[self_index]) + Counter(state.played_cards)
    pool_counts = full_deck - known  # Counter subtraction drops non-positive counts
    base_pool = list(pool_counts.elements())

    for _ in range(max_attempts):
        working_pool = base_pool[:]
        random.shuffle(working_pool)
        order = other_indices[:]
        random.shuffle(order)

        assignment = {}
        feasible = True
        for i in order:
            needed = len(state.hands[i])
            allowed = state.hand_info[i]
            candidates = [c for c in working_pool if c in allowed]
            if len(candidates) < needed:
                feasible = False
                break
            random.shuffle(candidates)
            chosen = candidates[:needed]
            assignment[i] = chosen
            for c in chosen:
                working_pool.remove(c)

        if feasible:
            new_state = deepcopy(state)
            for i in other_indices:
                new_state.hands[i] = assignment[i]
            return new_state

    raise RuntimeError(
        "determinize_state: no feasible joint hand assignment found in "
        f"{max_attempts} attempts. hand_info may be over-constrained, "
        "inconsistent, or the greedy sampler needs a smarter (e.g. "
        "backtracking / Hall's-theorem-based) assignment strategy."
    )