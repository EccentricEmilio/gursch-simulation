from statistics import mean
import random
from copy import deepcopy
import gursh

def determinize(state: gursh.State, self_index: int) -> list[int]:
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

    random.shuffle(unknown)
    return unknown[:hand_len]


def minimax(state: gursh.State) -> float:
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
            

def choose_move(state: gursh.State):
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

engine = gursh.Engine()
state = gursh.State.create_new_game()
print(state)

agents = [gursh.RandomAgent(), gursh.RandomAgent()]

while not state.is_game_over():
    current_player = state.current_player

    obs = state.get_observable_state(current_player)

    legal_actions = engine.get_legal_actions(state)
    action = agents[current_player].get_action(obs, legal_actions)

    print(f"Player {current_player} plays {action}")
    state = engine.apply_action(state, action)

print(f"Winner: Player {state.get_winner()}")