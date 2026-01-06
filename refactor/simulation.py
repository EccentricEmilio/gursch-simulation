from terminal_ui import TerminalUI
from state import *
from engine import GameEngine
from models import RandomPolicy, POLICIES
import pydealer
from constants import *
from copy import deepcopy 




class Simulation:
    def __init__(self, policies, default_settings=DEFAULT_SETTINGS):
        self.policies = policies
        self.settings = deepcopy(default_settings)

    def run_sim(self, player_count: int) -> GameResult:
        state = GameState(player_count, self.settings)
        engine = GameEngine(state, self.policies)

        state.deal_initial_hands()
        engine.determine_starting_index()

        while state.phase == 0:
            engine.process_turn() 
            engine.resolve_round() # determine round winner and update state
            engine.advance_state() # Check if game is over

        return self.to_result(state)
    
    def to_result(self, state) -> GameResult:
        policies = [str(policy) for policy in self.policies]
        return GameResult(
            state.players,
            policies,
            state.loser_score,
            state.ties
        )