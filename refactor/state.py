from functools import total_ordering
import pydealer 
from constants import *
from typing import Tuple, Any

@total_ordering
class Card:
    def __init__(self, value: str, suit: str):
        self.value = value
        self.int_value = POKER_VALUES[self.value]
        self.suit = suit
        #self.raw = self.value + self.suit[0]
        self.raw = self.value + " of " + self.suit
        self.abbrev = self.value + self.suit[0]
    
    def __eq__(self, other):
        if not isinstance(other, Card):
            return NotImplemented
        return self.int_value == other.int_value

    def __lt__(self, other):
        if not isinstance(other, Card):
            return NotImplemented
        return self.int_value < other.int_value
    
    def __repr__(self):
        return f"{self.abbrev}"

class Move:
    def __init__(self, cards: list):
        self.cards = tuple(cards)
    
    def __getitem__(self, index):
        return self.cards[index]

    def __repr__(self):
        str_cards = [repr(c) for c in self.cards]
        return f"Move({', '.join(str_cards)})"
    
    def __len__(self):
        return len(self.cards)
    
class RoundRecord:
    def __init__(self, round_index: int, game_phase: int, Turn):
        '''
        0 = SetupPhase, 1 = ThrowPhase, 2 = PlayPhase, 3 = GameIsOver
        # actions = current_turn
        {"player": list[Card] or Move}
        '''
        self.round_index = round_index
        self.game_phase = game_phase
        self.actions = actions
        
class ActionRecord:
    def __init__(self, player: str, turn_index: int, move: Any):
        self.player = player
        self.turn_index = turn_index
        self.move = move
        

class GameState:
    def __init__(self, player_count, settings: dict):
        self.settings = settings
        self.round_index = 0
        self.player_count = player_count
        self.board = []
        self.phase = 0 # 0 = SetupPhase, 1 = ThrowPhase, 2 = PlayPhase, 3 = GameIsOver
        self.throw_amount = 1
        self.current_round = {}
        #
        
        self.deck = pydealer.Deck() 
        self.deck.shuffle()
        
        self.loser_score = ()
        self.ties = []

        self.players = PLAYER_NAMES[0:self.player_count]
        self.players_hands = {p: [] for p in self.players} 
        self.starting_player_index = None
        self.active_player_index = None
        
        self.deal_initial_hands()
    
    def is_game(self):
        return self.phase < 3

    def return_cards(self, amount: int) -> list:
        if len(self.deck) < amount:
            raise ValueError
        card_stack = self.deck.deal(amount)
        new_card_stack = [Card(VALUE_MAP[c.value], c.suit) for c in card_stack.cards]
        return new_card_stack
    
    def deal_initial_hands(self):
        self.players_hands = {p: self.return_cards(self.settings["cards_per_hand"]) for p in self.players}
            
    def debug_set_hands(self, hands: dict):
        for player, hand in hands.items():
            self.players_hands[player] = hand

class GameResult:
    def __init__(self, players, policies, loser_score, ties, board):
        self.players = players
        self.policies = policies
        self.loser_score = loser_score
        self.ties = ties
        self.board = board
    
    def print_stats(self):
        pass