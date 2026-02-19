"""Simulation runner for batch game execution."""

from copy import deepcopy
from constants import DEFAULT_SETTINGS
from state import GameState, GameResult
from engine import GameEngine
from terminal_ui import TerminalUI


class Simulation:
    """Runs Gursch game simulations."""
    
    def __init__(self, policies, default_settings=DEFAULT_SETTINGS):
        self.policies = policies
        self.settings = deepcopy(default_settings)
    
    def run_sim(self, player_count: int) -> GameResult:
        """Run a single silent game."""
        state = GameState(player_count, self.settings)
        engine = GameEngine(state, self.policies)
        
        while state.is_game():
            engine.step()
        
        engine.calculate_losers()
        return self._to_result(state)
    
    def run_terminal_sim(self, player_count: int) -> GameResult:
        """Run a single game with terminal output."""
        state = GameState(player_count, self.settings)
        engine = GameEngine(state, self.policies)
        ui = TerminalUI(state)
        
        ui.print_setup()
        
        while state.is_game():
            engine.step()
        
        engine.calculate_losers()
        ui.print_sim()
        return self._to_result(state)
    
    def run_several_sim(self, count: int, player_count: int) -> list[GameResult]:
        """Run multiple games."""
        return [self.run_sim(player_count) for _ in range(count)]
    
    def _to_result(self, state: GameState) -> GameResult:
        """Convert game state to result."""
        policies = [str(p) for p in self.policies]
        return GameResult(
            state.players,
            policies,
            state.highest_score,
            state.losers,
            state.board
        )
