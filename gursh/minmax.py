from statistics import mean
from .state import State
from . import engine

def maxn(state: State) -> list[float]:
    '''
    N-player generalization of minimax. Instead of one scalar (player 0's
    advantage), each node's value is a vector with one utility per player.
    The player to move picks the action that maximizes *their own* entry in
    the vector, and the whole vector (everyone's utility under that choice)
    propagates upward.

    Note: unlike 2-player minimax, this does not support classic alpha-beta
    pruning. Bounding one player's value no longer bounds another's, since
    it's not a zero-sum relationship, so only weaker "shallow pruning" is
    available. Expect this to be noticeably more expensive per node than
    the 2-player case for the same branching factor and depth.
    '''
    if state.is_game_over():
        return state.get_utilities()

    player = state.current_player
    best_vector = None

    for action in engine.get_legal_actions(state):
        child_state = engine.apply_action(state, action)
        vector = maxn(child_state)
        if best_vector is None or vector[player] > best_vector[player]:
            best_vector = vector
    assert best_vector is not None, "No legal actions available for non-terminal state."

    return best_vector


def choose_move_maxn(state: State, simulations: int = 100) -> dict[int, float]:
    '''
    Determinized maxn move evaluation, from the perspective of whichever
    player is actually on the clock (state.current_player) - no hardcoded
    player index anywhere in this path.
    '''
    self_index = state.current_player
    legal_actions = engine.get_legal_actions(state)
    values = {action: [] for action in legal_actions}

    for _ in range(simulations):
        det_state = engine.determinize_state(state, self_index)

        for action in legal_actions:
            child_state = engine.apply_action(det_state, action)
            vector = maxn(child_state)
            # Only the acting player's own utility matters for their choice.
            values[action].append(vector[self_index])

    return {action: mean(vals) for action, vals in values.items()}


def test_choose_move_maxn(player_count: int = 3, hand_size: int = 4, simulations: int = 100):
    state = State.create_new_game(player_count=player_count, hand_size=hand_size)
    print(state)
    print(f"Acting player: {state.current_player}")
    values = choose_move_maxn(state, simulations=simulations)
    print(f"Values (from acting player's perspective): {values}")
    best_move = max(values, key=lambda k: values[k])
    print(f"Best move: {best_move}")