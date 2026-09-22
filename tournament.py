from gursh import engine
import gursh

state = gursh.State.create_new_game()
print(state)

agents = [gursh.RandomAgent(), gursh.MaxNAgent()]

while not state.is_game_over():
    current_player = state.current_player

    obs = state.get_observable_state(current_player)

    legal_actions = engine.get_legal_actions(state)
    action = agents[current_player].get_action(obs, legal_actions)
    if not action in legal_actions:
        raise ValueError(f"Illegal action {action} for player {current_player}. Legal actions: {legal_actions}")

    print(f"Player {current_player} plays {action}")
    state = engine.apply_action(state, action)

print(f"Utilities: {state.get_utilities()}")
