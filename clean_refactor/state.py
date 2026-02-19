"""Game state representation for Gursch card game."""

from functools import total_ordering
import pydealer 
from constants import *


@total_ordering
class Card:
    """Represents a single playing card with poker values."""
    
    def __init__(self, value: str, suit: str):
        self.value = value
        self.int_value = POKER_VALUES[self.value]
        self.suit = suit
        self.abbrev = self.value + self.suit[0]
    
    def __add__(self, other):
        return self.int_value + other.int_value
    
    def __radd__(self, other):
        return self.int_value if other == 0 else self.int_value + other
    
    def __eq__(self, other):
        if not isinstance(other, Card):
            return NotImplemented
        return self.int_value == other.int_value
    
    def __lt__(self, other):
        if not isinstance(other, Card):
            return NotImplemented
        return self.int_value < other.int_value
    
    def __repr__(self):
        return self.abbrev
    
    def __hash__(self):
        return hash((self.value, self.suit))


class Move:
    """Represents cards played together in a single action."""
    
    def __init__(self, cards: list[Card]):
        self.cards = tuple(cards)
        self.score = sum(self.cards)
    
    def return_true_score(self) -> int:
        """Calculate score with 7s wildcard rules.
        
        - Only 7s: sum all values
        - 7s + others: lowest non-7 value * number of cards
        - No 7s: sum all values
        """
        sevens = [c for c in self.cards if c.value == "7"]
        non_sevens = [c for c in self.cards if c.value != "7"]
        
        if sevens and non_sevens:
            return non_sevens[0].int_value * len(self.cards)
        return self.score
    
    def __getitem__(self, idx):
        return self.cards[idx]
    
    def __repr__(self):
        return f"Move({', '.join(repr(c) for c in self.cards)})"
    
    def __len__(self):
        return len(self.cards)
    
    def __hash__(self):
        return hash(self.cards)
    
    def __eq__(self, other):
        if not isinstance(other, Move):
            return False
        return self.cards == other.cards


class RoundRecord:
    """Records all actions in a single game round."""
    
    def __init__(self, index: int, game_phase: int, turns: list, 
                 players_hands: dict, starting_player: str = None):
        self.index = index
        self.game_phase = game_phase
        self.turns = turns
        self.players_hands = {p: list(h) for p, h in players_hands.items()}
        self.starting_player = starting_player
        
        # Determine round type
        self.type = "throw" if game_phase == THROW_PHASE else "play"
    
    def get_lowest_throw_num(self) -> int:
        if self.type != "throw":
            raise ValueError("Not a throw round")
        return min(t.throw_count for t in self.turns)


class TurnRecord:
    """Single player's move during a play round."""
    
    def __init__(self, player: str, turn_index: int, move: Move):
        self.player = player
        self.turn_index = turn_index
        self.move = move


class ThrowRecord:
    """Single player's throw action during a throw round."""
    
    def __init__(self, player: str, throw_count: int, thrown_cards: list):
        self.player = player
        self.throw_count = throw_count
        self.thrown_cards = thrown_cards


class GameState:
    """Holds all mutable game state."""
    
    def __init__(self, player_count: int, settings: dict):
        self.settings = settings
        self.round_index = 0
        self.player_count = player_count
        
        if self.player_count * self.settings["hand_size"] > 52:
            raise ValueError("Too many cards for deck")
        
        self.board = []
        self.phase = SETUP_PHASE
        self.current_round = None
        
        self.deck = pydealer.Deck()
        self.deck.shuffle()
        
        self.highest_score = -1
        self.losers = []
        
        self.players = PLAYER_NAMES[0:self.player_count]
        self.players_hands = {p: [] for p in self.players}
        self.player_zero = None
    
    def is_game(self) -> bool:
        """Check if game is still in progress."""
        return self.phase != GAMEOVER_PHASE
    
    def return_cards(self, amount: int) -> list[Card] | None:
        """Draw cards from deck."""
        if len(self.deck) < amount:
            return None
        
        cards = self.deck.deal(amount)
        return [Card(VALUE_MAP[c.value], c.suit) for c in cards.cards]
    
    def deal_initial_hands(self):
        """Deal starting hands to all players."""
        hand_size = self.settings["hand_size"]
        self.players_hands = {
            p: self.return_cards(hand_size) 
            for p in self.players
        }


class GameResult:
    """Result of a completed game."""
    
    def __init__(self, players, policies, highest_score, losers, board):
        self.players = players
        self.policies = policies
        self.highest_score = highest_score
        self.losers = losers
        self.board = board
