import gursh as gu


def run_tournament(silent: bool = True, hands = None, hand_size: int = 5):
    agents: list[gu.agents.Agent] = [
        gu.agents.MaxNAgent(), 
        gu.agents.MaxNAgent(), 
        gu.agents.MaxNAgent(),
    ]

    state = gu.state.create_new_state(player_count=len(agents), hand_size=hand_size)
    if hands is not None:
        state.hands = hands

    if not silent:
        print(state)

    while not state.is_game_over():
        current_player = state.current_player

        obs = state.get_observable_state(current_player)

        legal_actions = gu.engine.get_legal_moves(state)
        action = agents[current_player].get_action(obs, legal_actions)
        if not action in legal_actions:
            raise ValueError(f"Illegal action {action} for player {current_player}. Legal actions: {legal_actions}")

        if not silent:
            print(f"Player {current_player} plays {action}")

        state = gu.engine.apply_action(state, action)

    if not silent:
        print(f"Utilities: {gu.engine.get_utilities(state)}")

    return gu.engine.get_utilities(state)

def run_multiple_tournaments(num_tournaments: int = 10):
    results = []
    for i in range(num_tournaments):
        print(f"Running tournament {i+1}/{num_tournaments}")
        results.append(run_tournament(silent=True))
    mean_result = [sum(x) / len(x) for x in zip(*results)]
    print(f"Mean result over {num_tournaments} tournaments: {mean_result}")
    return results, mean_result

#run_multiple_tournaments(num_tournaments=100)
hands = [[7, 3, 8, 3], [7, 2, 4, 2], [7, 5, 12, 6]]
run_tournament(silent=False, hands=hands, hand_size=4)