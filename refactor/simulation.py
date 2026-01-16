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
        ui = TerminalUI(state)

        while state.is_game():
            engine.step()
        engine.calculate_losers()

        return self.to_result(state)


    def run_terminal_sim(self, player_count: int) -> GameResult:
        state = GameState(player_count, self.settings)
        engine = GameEngine(state, self.policies)
        ui = TerminalUI(state)

        while state.is_game():
            engine.step()
        engine.calculate_losers()
        ui.print_sim()

        return self.to_result(state)
    
    def to_result(self, state) -> GameResult:
        policies = [str(policy) for policy in self.policies]
        return GameResult(
            state.players,
            policies,
            state.highest_score,
            state.losers,
            state.board
        )