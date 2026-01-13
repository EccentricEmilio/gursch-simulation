from terminal_ui import TerminalUI
from state import *
from engine import GameEngine
from constants import *
from copy import deepcopy 

class Simulation:
    def __init__(self, policies, default_settings=DEFAULT_SETTINGS):
        self.policies = policies
        self.settings = deepcopy(default_settings)

    def run_sim(self, player_count: int) -> GameResult:
        state = GameState(player_count, self.settings)
        engine = GameEngine(state, self.policies)

        while state.is_game():
            engine.process_turn() 
            engine.resolve_round() # determine round winner and update state
            engine.advance_state() # Check if game is over

        return self.to_result(state)

    def run_terminal_sim(self, player_count: int) -> GameResult:
        state = GameState(player_count, self.settings)
        engine = GameEngine(state, self.policies)
        ui = TerminalUI()

        while state.is_game():
            print(state.phase, "PHASE")
            ui.print_game_state(state) # process each player's turn
            engine.process_turn()
            if state.phase == 1:
                ui.print_throw_turn(state)
            elif state.phase == 2:
                ui.print_players_choice(state)
            engine.resolve_round() # determine round winner and update state
            engine.advance_state() # Check if game is over

        ui.print_loser(state.loser_score, state.ties)
        return self.to_result(state)
    
    def to_result(self, state) -> GameResult:
        policies = [str(policy) for policy in self.policies]
        return GameResult(
            state.players,
            policies,
            state.loser_score,
            state.ties,
            state.board
        )