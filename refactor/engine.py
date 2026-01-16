from constants import *
from state import GameState, Card, Move, RoundRecord, TurnRecord, ThrowRecord
from models import *
from itertools import combinations

class GameEngine:
    def __init__(self, state: GameState, policies: list):
        self.state = state
        self.players_policies = {p: policies[self.state.players.index(p)] for p in self.state.players}
            
            
    def step(self):
        if self.state.phase == SETUP_PHASE:
            self.setup()
        elif self.state.phase == THROW_PHASE:
            self.process_throw_round()
        elif self.state.phase == PLAY_PHASE:
            self.start_round()
            self.play_rounds()
            self.end_round() 
        elif self.state.phase == GAMEOVER_PHASE:
            pass
        
    def setup(self):
        self.state.deal_initial_hands()
        
        # set starting player index
        winner_value = -1
        winner = None
        for p in self.state.players:
                hand = self.state.players_hands.get(p)
                int_value = hand[-1].int_value

                if int_value >= winner_value:
                    winner = p
                    winner_value = int_value
        self.state.player_zero = winner
        self.state.phase += 1


    def process_throw_round(self):
        '''       
        Docstring for process_throw_round
        
        :param self: Description
        '''
        throw_amounts = self.determine_throw_amounts()
        lowest_throw = min(throw_amounts)
        execute_throw = lowest_throw > 0
        
        self.state.current_round = RoundRecord(
            self.state.round_index, 
            THROW_PHASE,
            [],
            self.state.players_hands
        )

        if not self.check_deck(lowest_throw * self.state.player_count):
            execute_throw = False
        for i, p in enumerate(self.state.players):
            p_throw_amount = throw_amounts[i]
            thrown_cards = []
            
            if execute_throw:        
                thrown_cards = self.get_throw_cards(lowest_throw, p)
                self.swap_cards(thrown_cards, p)
                
            record = ThrowRecord(
                p,
                p_throw_amount,
                thrown_cards
            )
            
            self.state.current_round.turns.append(record)
        if not execute_throw:
            self.state.phase = PLAY_PHASE
        self.state.round_index += 1
        self.state.board.append(self.state.current_round)
    
    
    def swap_cards(self, swap_cards: list[Card], player: str):
        # Swap X amount of cards
        # swap_cards is cards in hand designated to be swapped
        new_cards = self.state.return_cards(len(swap_cards))
        if new_cards == None:
            self.state.phase = PLAY_PHASE
            return False
        
        hand = self.state.players_hands[player]
        # BUG, here we need to check cards equality based on suit and value
        # not just value, otherwise mulitiples of same values get removed
        # FIXED
        swap_card_abbrev = [c.abbrev for c in swap_cards]
        remaining_cards = [card for card in hand if card.abbrev not in swap_card_abbrev]
        new_hand = new_cards + remaining_cards
        self.state.players_hands[player] = new_hand
        return True 
    
    
    def determine_throw_amounts(self) -> list[int]:
        '''
        Create a list of players desired throw_amount,
        the lowest amount is the set amount.
        The list which is returned is in state.players order.
        
        '''
        players = self.state.players
        throw_amount_list = [self.players_policies[p].return_throw_amount(self.state, p) for p in players]
        return throw_amount_list
        
        
    def get_throw_cards(self, throw_amount: int, player: str) -> list[Card]:
        policy = self.players_policies[player]
        return policy.return_throw(self.state, player, throw_amount)
# -------------------------- THROW DONE -----------------------------

    def start_round(self):
        cur_hand_size = len(list(self.state.players_hands.values())[0]) 
        if cur_hand_size == self.state.settings["hand_size"]:
            # first play round
            starting_player = self.state.player_zero
        else:
            # This assumes current_round.turns is ordered correctly
            # possible BUG
            starting_player = self.return_starting_player(self.state.current_round.turns)

        self.state.current_round = RoundRecord(
            self.state.round_index,
            PLAY_PHASE,
            [],
            self.state.players_hands,
            starting_player
        )
    
    def play_rounds(self):
        starting_player = self.state.current_round.starting_player
        start_index = self.state.players.index(starting_player)
        round_order = self.state.players[start_index:] + self.state.players[:start_index]
        
        for p in round_order:
            self.apply_move(p, round_order)
        
        self.state.board.append(self.state.current_round)

    
    def apply_move(self, player: str, round_order: list[str]):
        policy = self.players_policies[player]
        legal_moveset = self.legal_moveset(player)
        
        move_played = policy.return_move(
            self.state, 
            player, 
            legal_moveset
        )
        
        turn_index = round_order.index(player)
        current_turn = TurnRecord(player, turn_index, move_played)
        
        for card in move_played:
            self.state.players_hands[player].remove(card)
        
        self.state.current_round.turns.append(current_turn)
        
        
    def end_round(self):
        '''
        if self.state.current_round.type == "throw":
            if self.state.current_round.get_lowest_throw_num( ) == 0:
                # Someone said 0
                self.return_starting_player(self.state.current_round.turns)
        elif self.state.current_round.type == "play":
            self.return_starting_player()
        '''
        self.state.round_index += 1
        if self.state.players_hands[self.state.player_zero] == []:
            self.state.phase += 1
        
    def calculate_losers(self):
        round = self.state.board[-1]
        turns = round.turns
        
        scores_by_player = {
            turn.player: turn.move.score
            for turn in turns
        }
        
        highest_score = max(scores_by_player.values())
        
        losers = [
            player
            for player, score in scores_by_player.items()
            if score == highest_score
        ]
        self.state.losers = losers
        self.state.highest_score = highest_score
        
# ---------------------------- RULES ------------------------------------
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
        if self.state.current_round.turns == []:
            return self.is_legal_lead(move)

        # 3. Response rules
        lead_move = self.state.current_round.turns[0].move
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
# ---------------------------- RULE LOGIC END ---------------------

    def return_starting_player(self, turns: list[TurnRecord])-> str:
        winner = None
        winner_value = -1
    
        # This block currently only handles the last card played in the round
        for turn in turns:
            int_value = turn.move[0].int_value
            
            if int_value >= winner_value:
                winner = turn.player
                winner_value = int_value
        return winner


    def sort_hands(self):
        for p, h in self.state.players_hands.items():
            h.sort()

    def swap_hand(self, player: str):
        # NOT IMPLEMENTED
        # Swap all five, only allowed once at the beginning of the game
        new_cards = self.state.return_cards(5)
        self.state.players_hands[player] = new_cards
    
    def check_deck(self, amount: int):
        return amount <= len(self.state.deck)