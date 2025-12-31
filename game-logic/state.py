import pydealer 
from constants import *

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

    def deal_initial_hands(self):
        for hand in self.players_hands.values():
            card_stack = self.deck.deal(self.TOTAL_CARDS_PER_HAND)
            hand.extend(c.abbreviate() for c in card_stack)
            
    def debug_set_hands(self, hands: dict):
        for player, hand in hands.items():
            self.players_hands[player] = hand