from copy import deepcopy
from collections import Counter
import itertools
import random
from .state import State


def get_legal_moves(state: State) -> list[tuple[int, ...]]:
    moves: list[tuple[int, ...]] = []
    player_hand = state.hands[state.current_player] 
    if state.played_this_round == 0:
        # Lead
        counts = Counter(player_hand)
        for rank in sorted(counts):
            for k in range(1, counts[rank] + 1):
                moves.append((rank,) * k)
    else:
        # Response
        # Both the lowest, and all possible moves that are higher than the current highest value are legal
        # Lowest
        lowest_move = tuple(sorted(player_hand)[:state.move_length])
        moves.append(lowest_move)

        # Above or matching the highest value
        above_highest = [c for c in player_hand if c >= state.highest_value]
        moves_above_highest = []
        for r in range(len(above_highest) + 1):
            for comb in itertools.combinations(above_highest, r):
                if len(comb) == state.move_length and comb not in moves_above_highest:
                    moves_above_highest.append(tuple(comb))
        moves.extend(moves_above_highest)
    return moves

def apply_action(state: State, move: tuple[int, ...]) -> State:
    '''
    Remove move from current_player's hand
    Update .highest_value and .round_leader if necessary
    Update .hand_info for current_player if necessary
    Update .played_moves
    Update .move_length if necessary
    Increment .current_player and .played_this_round
    '''
    next_state = state.copy()
    for c in move:
        next_state.hands[next_state.current_player].remove(c)
    next_state.played_moves.append(move)

    if next_state.played_this_round == 0:
        # Lead move, update move_length
        next_state.move_length = len(move)
    
    if all([(c > next_state.highest_value) for c in move]):
        # Response over highest value, or leading the round
        # Update highest_value and assign new eventual winner
        next_state.highest_value = max(move)
        next_state.round_leader = next_state.current_player
    else:
        # Played their smallest card and is not the first round
        # max(move) == lowest card left in hand
        next_state.hand_info[next_state.current_player] = set(range(max(move), 15))

    next_state.played_this_round += 1

    if next_state.played_this_round == len(next_state.hands):
        if state.is_game_over():
            # If game is over
            # Dont change current_player so that get_utilites knows the round order
            return next_state

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
    known = Counter(state.hands[self_index]) + Counter([v for move in state.played_moves for v in move])
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

def get_utilities(state: State):
    '''
    Assumes is_game_over == True. Returns one utility value per player

    Payment model: whoever holds the highest final card (value V) is the
    loser ("gurka") and pays V to every other player. If k players tie
    for the highest card, they share that cost evenly: each winner still
    receives the same total V (not k*V), but each of the k tied losers
    only pays V/k to each winner, rather than each paying the full V.
    If every player ties (k == n, no winners), no payment occurs and
    every utility is 0.0. This is a zero-sum transfer either way:
    sum(get_utilities()) == 0.0 always, which is a good sanity check.
    '''

    n = len(state.hands)
    # [(2, (9, 9)), (3, (10, 11)), (0, (2, 7)), (1, (11, 6))]
    assigned_moves = [ 
        ((state.current_player - (n - 1 - i)) % n, move)
        for i, move in enumerate(state.played_moves[-n:])
    ]
    # [(0, (2, 7)), (1, (11, 6)), (2, (9, 9)), (3, (10, 11))]
    sorted_moves = sorted(assigned_moves, key = lambda x: x[0])
    # [9, 17, 18, 21]
    move_values = [sum(m[1]) for m in sorted_moves]
    max_value = max(move_values)

    losers = [i for i in range(n) if move_values[i] == max_value]
    k = len(losers)
    winners_count = n - k

    utilities = [0.0] * n
    if winners_count == 0:
        # Everyone tied - no winners to pay, nothing changes hands.
        return utilities

    share_per_loser = max_value / k
    for i in range(n):
        if i in losers:
            utilities[i] = -share_per_loser * winners_count
        else:
            utilities[i] = max_value

    return utilities 