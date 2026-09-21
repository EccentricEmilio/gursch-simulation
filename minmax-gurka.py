from statistics import mean
import random
from copy import deepcopy
from gursh import engine, State, state


def minimax(state: State) -> float:
    if state.is_game_over():
        return state.get_winner()
 
    if state.current_player == 0:
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


def choose_move(state: State) -> dict[int, list[float]]:
    legal_actions = engine.get_legal_actions(state)
    values = {action: [] for action in legal_actions}

    for action in legal_actions:
        child_state = engine.apply_action(state, action)
        eval = minimax(child_state)

        values[action].append(eval)
    return values

def choose_move_determinized(state: State, simulations: int = 100) -> dict[int, float]:
    legal_actions = engine.get_legal_actions(state)
    values = {action: [] for action in legal_actions}

    for _ in range(simulations):
        det_state = engine.determinize_state(state, 1)
        for action in legal_actions:
            child_state = engine.apply_action(det_state, action)
            eval = minimax(child_state)

            values[action].append(eval)

    values = {action: mean(values[action]) for action in legal_actions}

    return values



def test_highest_choose_move():
    flag = False
    for _ in range(100):
        state = State.create_new_game()
        values = choose_move_determinized(state)
        best_move = max(values, key=values.get)
        if best_move != max(state.hands[0]):
            flag = True
            print(f"State: {state}")
            print(f"Values: {values}")
    if flag:
        print("Test failed: The best move was not the highest card in hand.")
    else:
        print("Test passed: The best move was the highest card in hand.")


def test_choose_move():
    state = State.create_new_game(hand_size = 5)
    values = choose_move_determinized(state)
    print(f"State: {state}")
    print(f"Values: {values}")



test_choose_move()







