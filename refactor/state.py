from functools import total_ordering
import pydealer 
from constants import *

@total_ordering
class Card:
    def __init__(self, value: str, suit: str):
        self.value = value
        self.int_value = POKER_VALUES[self.value]
        self.suit = suit
        #self.raw = self.value + self.suit[0]
        self.raw = self.value + " of " + self.suit
        self.abbrev = self.value + self.suit[0]
    
    def __add__(self, obj_2):
        return self.int_value + obj_2.int_value
    
    def __radd__(self, other):
        if other == 0:
            return self.int_value
        else:
            return self.int_value + other
    
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
    def __init__(self, cards: list[Card]):
        self.cards = tuple(cards)
        self.score = sum(self.cards)
        
    def return_true_score(self) -> int:
        sevens = [c for c in self.cards if c.value == "7"]
        non_sevens = [c for c in self.cards if c.value != "7"]
        
        # Default score
        score = self.score
        
        if sevens and not non_sevens:
            # Only sevens
            # Nothing needs to be done
            pass
        elif sevens and non_sevens:
            # sevens and non_sevens
            score = non_sevens[0].int_value  * len(self.cards)
        elif not sevens and non_sevens:
            # No sevens, nothing needs to be done.
            pass    
        return score
    
    def __getitem__(self, index):
        return self.cards[index]

    def __repr__(self):
        str_cards = [repr(c) for c in self.cards]
        return f"Move({', '.join(str_cards)})"
    
    def __len__(self):
        return len(self.cards)
    
class RoundRecord:
    def __init__(self, 
                 index: int, 
                 game_phase: int, 
                 turns: list, 
                 players_hands: dict,
                 starting_player: str = None):
        '''
        0 = SetupPhase, 1 = ThrowPhase, 2 = PlayPhase, 3 = GameIsOver
        if self.type == "throw":
            turns: list[ThrowRecord]
        if self.type == "play":
            turns: list[TurnRecord]
        '''
        self.type = None
        self.index = index
        self.game_phase = game_phase
        self.turns = turns
        if game_phase == 1:
            self.type = "throw"
        elif game_phase == 2:
            self.type = "play"
        self.players_hands = {p: list(h) for p, h in players_hands.items()}
        self.starting_player = starting_player
    
    def __repr__(self):
        return str(self.turns)
    
    def get_lowest_throw_num(self):
        if self.type == "play":
            raise ValueError
        return min([throw.throw_count for throw in self.turns])
            
        
class TurnRecord:
    def __init__(self, player: str, turn_index: int, move: Move):
        self.player = player
        self.turn_index = turn_index
        self.move = move
        
        
    def __repr__(self):
        return self.player + " " + str(self.move)
        
class ThrowRecord:
    def __init__(self, player: str, throw_count: int, thrown_cards: list):
        self.player = player
        self.throw_count = throw_count
        self.thrown_cards = thrown_cards
    
    def __repr__(self):
        return self.player + " " + str(self.thrown_cards)
        

class GameState:
    def __init__(self, player_count, settings: dict):
        self.settings = settings
        self.round_index = 0
        self.player_count = player_count
        if self.player_count * self.settings["hand_size"] > 52:
            raise ValueError
        self.board = []
        self.phase = SETUP_PHASE
        self.current_round: RoundRecord = None
        
        self.deck = pydealer.Deck() 
        self.deck_empty = False
        self.deck.shuffle()
        
        self.highest_score = -1
        self.losers = []

        self.players = PLAYER_NAMES[0:self.player_count]
        self.players_hands = {p: [] for p in self.players} 
        self.player_zero = None
        
    
    def is_game(self):
        return self.phase != GAMEOVER_PHASE

    def return_cards(self, amount: int) -> list[Card] | None:
        if len(self.deck) < amount:
            return None
        
        card_stack = self.deck.deal(amount)
        return [Card(VALUE_MAP[c.value], c.suit) for c in card_stack.cards]


    def deal_initial_hands(self):
        self.players_hands = {p: self.return_cards(self.settings["hand_size"]) for p in self.players}
            
    def debug_set_hands(self, hands: dict):
        for player, hand in hands.items():
            self.players_hands[player] = hand

class GameResult:
    def __init__(self, players, policies, highest_score, losers, board):
        self.players = players
        self.policies = policies
        self.highest_score = highest_score
        self.losers = losers
        self.board = board
    
    def print_stats(self):
        pass
    
    
    
    
    
#move = Move([Card("7", "H"), Card("7","S"), Card("7","S"), Card("7","H"), Card("T","C")])
#print(move.return_true_score())
