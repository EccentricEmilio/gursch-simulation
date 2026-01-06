from terminal_ui import TerminalUI
from state import GameState
from engine import GameEngine
from models import RandomPolicy
import pydealer
from constants import *

player1 = RandomPolicy()
player2 = RandomPolicy()
player3 = RandomPolicy()

policies = [
    player1,
    player2,
    player3
]

def run_terminal_game():
    state = GameState()
    engine = GameEngine(state, policies)
    ui = TerminalUI()

    state.deal_initial_hands()
    #state.debug_set_hands(PLAYERS_HANDS_DEBUG)  # For testing purposes
    # Deck will contain duplicate cards if using debug hands
    engine.determine_starting_index()
    ui.print_game_state(state.turn_index, state.players_hands, 
                        initial_setup=True, starting_player=state.players[state.starting_player_index])
    # 0 is TEMPORARY 
    while state.phase == 0:
        engine.process_turn()
        ui.print_players_choice(state)
        engine.resolve_round() # determine round winner and update state
        ui.print_game_state(state.turn_index, state.players_hands) # process each player's turn
        engine.advance_state() # Check if game is over

    ui.print_loser(state.loser_score, state.ties)
if __name__ == "__main__":
    run_terminal_game()