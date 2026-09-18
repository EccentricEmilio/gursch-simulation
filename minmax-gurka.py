from statistics import mean
import random
from copy import deepcopy
from gursh import engine, State

def determinize(state: State, self_index: int) -> list[int]:
    if self_index == 0:
        enemy_index = 1
    else:
        enemy_index = 0

    hand_len = len(state.hands[enemy_index])

    unknown = list(state.hand_info[enemy_index]) * 4

    for card in state.hands[self_index] + state.played_cards:
        if card in unknown:
            unknown.remove(card)

    random.shuffle(unknown)
    return unknown[:hand_len]


def minimax(state: State) -> float:
    if state.is_game_over():
        return state.get_winner()
 
    if state.current_player==0:
        maxEval = -2

        legal_actions = engine.get_legal_actions(state)
        for action in legal_actions:
            child_state = engine.apply_action(state, action)

            eval = minimax(child_state)
            maxEval = max(maxEval, eval)
        return maxEval

    else:
        minEval = +2

        legal_actions = engine.get_legal_actions(state)
        for action in legal_actions:
            child_state = engine.apply_action(state, action)

            eval = minimax(child_state)
            minEval = min(minEval, eval)
        return minEval

state = State.create_new_game()

eval = minimax(state)

print(state)
print(eval)