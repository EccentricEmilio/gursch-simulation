from terminal_ui import TerminalUI
from state import GameState
from engine import GameEngine
from models import RandomPolicy
import pydealer
from simulation import Simulation
from constants import *
'''
policies = [
    RandomPolicy(),
    RandomPolicy(),
    RandomPolicy()
]

def run_terminal_game():
    state = GameState()
    engine = GameEngine(state, policies)
    ui = TerminalUI()

    state.deal_initial_hands()
    #state.debug_set_hands(PLAYERS_HANDS_DEBUG)  # For testing purposes
    # Deck will contain duplicate cards if using debug hands
    engine.determine_starting_index()
    # 0 is TEMPORARY 
    while state.phase == 0:
        ui.print_game_state(state.turn_index, state.players_hands, state.players[state.starting_player_index]) # process each player's turn
        engine.process_turn()
        ui.print_players_choice(state)
        engine.resolve_round() # determine round winner and update state
        engine.advance_state() # Check if game is over

    ui.print_loser(state.loser_score, state.ties)
if __name__ == "__main__":
    run_terminal_game()
'''

player_count = 4
settings = {}
random_policies = [RandomPolicy()] * 4

default_sim = Simulation(random_policies)



if __name__ == "__main__":
    result = default_sim.run_sim(player_count)

    print("Players:", result.players)
    print("Policies:", result.policies)
    print("Loser Score:", result.loser_score)
    print("Ties:", result.ties)
