from constants import *
from state import GameState, Card, Move
from models import *
from itertools import combinations
from itertools import groupby
  
class GameEngine:
    def __init__(self, state: GameState, policies: list):
        self.state = state
        

        self.players_policies = {p: policies[self.state.players.index(p)] for p in self.state.players}
        
    def run(self):
        # Run game?
        pass

    def swap_hand(self, player):
        # Swap all five, only allowed once at the beginning of the game
        new_cards = self.state.return_cards(5)
        self.state.players_hands[player] = new_cards
        return

    def swap_cards(self, amount, player):
        # Swap X amount of cards
        new_cards = self.state.return_cards(amount)
        self.state.players_hands[player] = new_cards
    
    def swap_phase(self):
        return



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

    def validate_player_input(self, player, chosen_cards):
        starting_player = self.state.players[self.state.starting_player_index]
        player_hand = self.state.players_hands[player]
        player_hand_values = sorted([POKER_VALUES[c[0]] for c in player_hand])
        if self.state.active_player_index == self.state.starting_player_index:
            currently_starter = True
        else:
            currently_starter = False
        
        if not currently_starter:
            # The cards played by starting_player
            starting_players_cards = self.state.current_round.get(starting_player, [])
            
            
        hand = [c.upper() for c in self.show_hand(player)]
        if len(chosen_cards) == 0:
            return False, ERROR_MESSAGES["NoCards"]
        if any(c not in hand for c in chosen_cards):
            return False, ERROR_MESSAGES["InvalidCard"]
        if len(chosen_cards) != len(set(chosen_cards)):
            return False, ERROR_MESSAGES["DuplicateCards"]
        if not currently_starter:
            if len(chosen_cards) != len(self.state.current_round[starting_player]):
                return False, ERROR_MESSAGES["MismatchedCount"]
        
        values = [POKER_VALUES[c[0]] for c in chosen_cards]
        if currently_starter:
            if len(set(values)) != 1:
                return False, ERROR_MESSAGES["DifferentValues"]
        if not currently_starter:
            starting_values = [POKER_VALUES[c[0]] for c in starting_players_cards]
            if NORMAL_SETTINGS["ResponseRequiresDuplicates"]:
                if values.count(values[0]) < starting_values.count(starting_values[0]):
                    return False, ERROR_MESSAGES["DifferentValues"]
                
        # If all checks pass, now check that value is allowed
        # compared to starting player's cards
        # Available variables for reference
        # chosen_cards - player - values 
        # starting_player - starting_values - starting_player_cards
        if not currently_starter:
            value_to_match = starting_values[0]
            # count is used for comparing values when multiple cards is played
            count = len(chosen_cards)
            for v in values:
                if value_to_match > v and v > min(player_hand_values):
                    return False, ERROR_MESSAGES["DisallowedValue"]
                if count != 1:
                    count -= 1
                    del player_hand_values[0]
        return True, None

    def show_hand(self, player_name):
        hand = self.state.players_hands[player_name]
        return hand

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
        # Prints should be handled outside engine
        print("Round " + str(self.state.turn_index) + " winner is " + self.state.players[self.state.starting_player_index])
        print("Current round results:" + str(self.state.current_round))
    
    def advance_state(self):
        if self.state.players_hands[self.state.players[0]] == []:
            self.state.phase += 1
        
            player_scores = []
            for player, cards in self.state.current_round.items():
                values = [c.int_value for c in cards]
                score = sum(values)
                player_score = (player, score)
                player_scores.append(player_score)
            scores = [ps[1] for ps in player_scores]
            if scores.count(max(scores)) > 1:
                ties = []
                for p, s in player_scores:
                    if s == max(scores):
                        ties.append(p)
                self.state.ties = ties
            else:
                highest_score = max(scores)
                for p, s in player_scores:
                    if s == highest_score:
                        loser = p
                self.state.loser_score = (loser, highest_score)
      
'''          
state = GameState({"player_count": 2})
state.deal_initial_hands()
policies = [HumanPolicy, HumanPolicy]
boi = GameEngine(state, policies)

BASJ = boi.generate_valid_moveset(state.players_hands["Abraham"], [7], False)
print([c.abbrev for c in state.players_hands["Abraham"]])
print([c.abbrev for c in BASJ])
'''