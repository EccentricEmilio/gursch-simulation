import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from engine import GameEngine
from state import GameState, Card
from unittest.mock import MagicMock

@pytest.fixture
def sample_state():
    # Skapa en minimal GameState med 2 spelare
    state = GameState(players=["Alice", "Bob"], settings={"hand_size":5})
    
    # Ge spelarna enkla kort
    state.players_hands = {
        "Alice": [Card("7", "S"), Card("9", ""), Card("2", "♦")],
        "Bob":   [Card("3", "♥"), Card("5", "♠"), Card("7", "♣")]
    }
    state.deck = [Card(str(v), s) for v in range(1,14) for s in "♠♥♦♣"]
    state.phase = 0
    state.round_index = 0
    return state

@pytest.fixture
def dummy_policy():
    # En enkel policy som alltid returnerar samma move / throw
    class Policy:
        def return_throw_amount(self, state, player):
            return 1
        def return_throw(self, state, player, amount):
            return state.players_hands[player][:amount]
        def return_move(self, state, player, legal_moveset):
            # Returnera första möjliga move
            return next(iter(legal_moveset))
    return Policy()

@pytest.fixture
def engine(sample_state, dummy_policy):
    policies = [dummy_policy, dummy_policy]
    return GameEngine(sample_state, policies)
