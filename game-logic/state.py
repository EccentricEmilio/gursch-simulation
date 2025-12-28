import pydealer 
from constants import *

class GameState:
    def __init__(self):
        self.TOTAL_CARDS_PER_HAND = CUSTOM_RULES["cards_per_hand"]
        self.turn_index = 0
        self.player_count = CUSTOM_RULES["player_count"]
        self.board = []
        self.game_is_over = False
        self.round_is_over = False
        self.current_round = {}
        self.deck = pydealer.Deck() 
        self.deck.shuffle()
        self.loser_score = None
        self.ties = None

        self.players = PLAYER_NAMES[0:CUSTOM_RULES["player_count"]]
        self.players_hands = {p: [] for p in self.players} 
        self.starting_player_index = None
        self.active_player_index = None

    def deal_initial_hands(self):
        for hand in self.players_hands.values():
            card_stack = self.deck.deal(self.TOTAL_CARDS_PER_HAND)
            hand.extend(c.abbreviate() for c in card_stack)
            
    def debug_set_hands(self, hands: dict):
        for player, hand in hands.items():
            self.players_hands[player] = hand