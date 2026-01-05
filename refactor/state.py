from functools import total_ordering
import pydealer 
from constants import *
from typing import Tuple

@total_ordering
class Card:
    def __init__(self, value: str, suit: str):
        self.value = value
        self.int_value = POKER_VALUES[self.value]
        self.suit = suit
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
        return self.raw

class Move:
    def __init__(self, cards: list):
        self.cards = list(cards)
    
    def __repr__(self):
        return f"Move({self.cards})"

class GameState:
    def __init__(self, settings: dict = {}):
        self.settings = NORMAL_SETTINGS
        for rule_key, rule_value in settings.items():
            self.settings[rule_key] = rule_value

        self.TOTAL_CARDS_PER_HAND = self.settings["cards_per_hand"]
        self.turn_index = 0
        self.player_count = self.settings["player_count"]
        self.board = []
        self.phase = 0 # 0 = SwitchPhase, 1 = PlayPhase, 2 = GameIsOver
        self.current_round = {}
        
        self.deck = pydealer.Deck() 
        self.deck.shuffle()
        
        self.loser_score = -1
        self.ties = []

        self.players = PLAYER_NAMES[0:self.settings["player_count"]]
        self.players_hands = {p: [] for p in self.players} 
        self.starting_player_index = None
        self.active_player_index = None

    def return_cards(self, amount: int) -> list:
        if len(self.deck) < amount:
            raise ValueError
        card_stack = self.deck.deal(amount)
        new_card_stack = [Card(VALUE_MAP[c.value], c.suit[0]) for c in card_stack.cards]
        return new_card_stack
    
    def deal_initial_hands(self):
        self.players_hands = {p: self.return_cards(self.TOTAL_CARDS_PER_HAND) for p in self.players}
            
    def debug_set_hands(self, hands: dict):
        for player, hand in hands.items():
            self.players_hands[player] = hand
            
#boi = GameState()
#boi.deal_initial_hands()
#for p, h in boi.players_hands.items():
#    print(p, [c.value for c in h])
