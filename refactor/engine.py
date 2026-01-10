from constants import *
from state import GameState, Card, Move, PLAYERS_HANDS_DEBUG
from models import *
from itertools import combinations
from itertools import groupby
  
class GameEngine:
    def __init__(self, state: GameState, policies: list):
        self.state = state
        self.players_policies = {p: policies[self.state.players.index(p)] for p in self.state.players}
        
    def swap_hand(self, player: str):
        # Swap all five, only allowed once at the beginning of the game
        new_cards = self.state.return_cards(5)
        self.state.players_hands[player] = new_cards

    def swap_cards(self, swap_cards: list[Card], player: str):
        # Swap X amount of cards
        # swap_cards is cards in hand designated to be swapped
        swap_card_abbrev = [c.abbrev for c in swap_cards]
        new_cards = self.state.return_cards(len(swap_cards))
        hand = self.state.players_hands[player]
        # BUG, here we need to check cards equality based on suit and value
        # not just value, otherwise mulitiples of same values get removed
        remaining_cards = [card for card in hand if card.abbrev not in swap_card_abbrev]
        new_hand = new_cards + remaining_cards
        self.state.players_hands[player] = new_hand
    
    def swap_phase(self):
        
        pass
    
    def process_0_turn(self):
        pass
        
    def process_turn(self):
        self.state.current_round = {}
        
        self.state.active_player_index = self.state.starting_player_index
        active_player = self.state.players[self.state.active_player_index]
        starting_player = self.state.players[self.state.starting_player_index]
        players_order = self.state.players[self.state.active_player_index:]
        players_order.extend(self.state.players[:self.state.active_player_index])

        for p in players_order:
            policy = self.players_policies[p]

            legal_moveset = self.legal_moveset(p)

            move_played = policy.return_move(
                self.state, 
                p, 
                legal_moveset
            )
            self.state.current_round[p] = move_played

            # remove cards
            for card in move_played:
                self.state.players_hands[p].remove(card)

            self.state.active_player_index += 1
            if self.state.active_player_index >= len(self.state.players):
                self.state.active_player_index = 0
            active_player = self.state.players[self.state.active_player_index]
        self.state.board.append(self.state.current_round)

    def is_legal_lead(self, move: Move) -> bool:
        # Check is move contains only duplicates
        values = {c.value for c in move.cards}
        if len(values) != 1:
            return False
        # Move is legal
        return True
    
    def is_legal_response(self, move: Move, lead_move: Move, player: str) -> bool:
        # Check for matching value or lowest card
        lead_value = lead_move[0].int_value
        
        hand_sorted = sorted(
            self.state.players_hands[player],
            key=lambda c: c.int_value
        )
        move_values = [c.int_value for c in move.cards]
        
        low_cards = [v for v in move_values if v < lead_value]
        low_count = len(low_cards)
                
        allowed_low_cards = hand_sorted[:low_count]
        
        for card in move.cards:
            if card.int_value >= lead_value:
                continue
            if card in allowed_low_cards:
                continue
            return False
        
        # Check responce length matches length of lead_move
        if len(move) != len(lead_move):
            return False
        
        return True
    
    def is_legal_move(self, player: str, move: Move) -> bool:
        # 1. Player must own the cards
        if not all(c in self.state.players_hands[player] for c in move.cards):
            return False

        # 2. First player rules
        if not self.state.current_round:
            return self.is_legal_lead(move)

        # 3. Response rules
        lead_move = list(self.state.current_round.values())[0]
        return self.is_legal_response(move, lead_move, player) 

    def legal_moveset(self, player: str):
        moveset = set()
        test_moveset = set()
        hand = self.state.players_hands[player]
        for r in range(1, len(hand) + 1):
            for combo in combinations(hand, r):
                move = Move(combo)
                if self.is_legal_move(player, move):
                    moveset.add(move)
                test_moveset.add(move)
        return moveset

    def determine_starting_index(self):
        winner = None
        winner_value = -1
        
        if self.state.turn_index == 0:
            for p in self.state.players:
                hand = self.state.players_hands.get(p)
                int_value = hand[-1].int_value

                if int_value >= winner_value:
                    winner = p
                    winner_value = int_value

        # This block currently only handles the last card played in the round
        if self.state.turn_index > 0:
            for player, Move in self.state.current_round.items():
                int_value = Move[0].int_value

                if int_value >= winner_value:
                    winner = player
                    winner_value = int_value
        
        winner_index = self.state.players.index(winner)
        self.state.starting_player_index = winner_index
        self.state.active_player_index = winner_index
            
    def resolve_round(self):
        # Determine round winner and update state
        self.state.turn_index += 1
        self.determine_starting_index()

    
    def advance_state(self):
        if self.state.players_hands[self.state.players[0]] == []:
            self.state.phase += 1
        
            player_scores = []
            for player, move in self.state.current_round.items():
                values = [c.int_value for c in move]
                score = sum(values)
                player_score = (player, score)
                player_scores.append(player_score)
            scores = [ps[1] for ps in player_scores]
            highest_score = max(scores)
            for p, s in player_scores:
                if s == highest_score:
                    loser = p
            self.state.loser_score = (loser, highest_score)
            if scores.count(max(scores)) > 1:
                ties = []
                for p, s in player_scores:
                    if s == max(scores):
                        ties.append(p)
                self.state.ties = ties