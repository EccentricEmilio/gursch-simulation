"""Game engine - handles game flow and rule validation."""

from itertools import combinations
from constants import *
from state import GameState, Card, Move, RoundRecord, TurnRecord, ThrowRecord


class GameEngine:
    """Executes game logic and enforces rules."""
    
    def __init__(self, state: GameState, policies: list):
        self.state = state
        # Map players to their decision policies
        self.players_policies = {
            p: policies[state.players.index(p)] for p in state.players
        }
    
    def step(self):
        """Execute one phase step."""
        if self.state.phase == SETUP_PHASE:
            self._setup()
        elif self.state.phase == THROW_PHASE:
            self._process_throw_round()
        elif self.state.phase == PLAY_PHASE:
            self._start_round()
            self._play_round()
            self._end_round()
    
    def _setup(self):
        """Deal initial hands and determine starting player."""
        self.state.deal_initial_hands()
        
        # Starting player = highest card in initial hand
        highest_value = -1
        for player in self.state.players:
            hand = self.state.players_hands[player]
            card_value = hand[-1].int_value
            if card_value >= highest_value:
                self.state.player_zero = player
                highest_value = card_value
        
        self.state.phase += 1
    
    def _process_throw_round(self):
        """Execute throw phase."""
        throw_amounts = self._determine_throw_amounts()
        lowest_throw = min(throw_amounts)
        
        # First round: only player_zero's choice matters
        if self.state.round_index == 0:
            idx = self.state.players.index(self.state.player_zero)
            lowest_throw = throw_amounts[idx]
        
        execute_throw = lowest_throw > 0
        
        # Create round record
        self.state.current_round = RoundRecord(
            self.state.round_index,
            THROW_PHASE,
            [],
            self.state.players_hands
        )
        
        # Check deck has enough cards
        if not self._check_deck(lowest_throw * self.state.player_count):
            execute_throw = False
        
        # Process each player's throw
        for i, player in enumerate(self.state.players):
            thrown_cards = []
            
            if execute_throw:
                thrown_cards = self._get_throw_cards(lowest_throw, player)
                self._swap_cards(thrown_cards, player)
            
            record = ThrowRecord(player, throw_amounts[i], thrown_cards)
            self.state.current_round.turns.append(record)
        
        if not execute_throw:
            self.state.phase = PLAY_PHASE
        
        self.state.round_index += 1
        self.state.board.append(self.state.current_round)
    
    def _swap_cards(self, swap_cards: list[Card], player: str) -> bool:
        """Replace player's cards with new ones from deck."""
        new_cards = self.state.return_cards(len(swap_cards))
        if new_cards is None:
            self.state.phase = PLAY_PHASE
            return False
        
        hand = self.state.players_hands[player]
        swap_abbrevs = {c.abbrev for c in swap_cards}
        remaining = [c for c in hand if c.abbrev not in swap_abbrevs]
        
        self.state.players_hands[player] = new_cards + remaining
        return True
    
    def _determine_throw_amounts(self) -> list[int]:
        """Get each player's desired throw amount."""
        return [
            self.players_policies[p].return_throw_amount(self.state, p) 
            for p in self.state.players
        ]
    
    def _get_throw_cards(self, amount: int, player: str) -> list[Card]:
        """Get cards player wants to throw."""
        policy = self.players_policies[player]
        return policy.return_throw(self.state, player, amount)
    
    def _start_round(self):
        """Initialize a play round."""
        hand_size = self.state.settings["hand_size"]
        current_hand = len(list(self.state.players_hands.values())[0])
        
        # First play round uses player_zero
        if current_hand == hand_size:
            starting_player = self.state.player_zero
        else:
            # Subsequent rounds: previous round winner (highest card)
            starting_player = self._return_starting_player(
                self.state.current_round.turns
            )
        
        self.state.current_round = RoundRecord(
            self.state.round_index,
            PLAY_PHASE,
            [],
            self.state.players_hands,
            starting_player
        )
    
    def _play_round(self):
        """Play one round: all players take turns."""
        starting_player = self.state.current_round.starting_player
        start_idx = self.state.players.index(starting_player)
        
        round_order = self.state.players[start_idx:] + self.state.players[:start_idx]
        
        for player in round_order:
            self._apply_move(player, round_order)
        
        self.state.board.append(self.state.current_round)
    
    def _apply_move(self, player: str, round_order: list[str]):
        """Execute one player's move."""
        policy = self.players_policies[player]
        legal_moveset = self.legal_moveset(player)
        
        move = policy.return_move(self.state, player, legal_moveset)
        
        turn_idx = round_order.index(player)
        turn_record = TurnRecord(player, turn_idx, move)
        
        for card in move.cards:
            self.state.players_hands[player].remove(card)
        
        self.state.current_round.turns.append(turn_record)
    
    def _end_round(self):
        """Finalize round; check if game is over."""
        self.state.round_index += 1
        
        if not self.state.players_hands[self.state.player_zero]:
            self.state.phase = GAMEOVER_PHASE
    
    def calculate_losers(self):
        """Calculate final scores and determine loser(s)."""
        final_round = self.state.board[-1]
        scores = {}
        
        for turn in final_round.turns:
            score = turn.move.return_true_score()
            scores[turn.player] = score
        
        highest = max(scores.values())
        self.state.losers = [p for p, s in scores.items() if s == highest]
        self.state.highest_score = highest
    
    # ==================== RULES ====================
    
    def is_legal_lead(self, move: Move) -> bool:
        """Valid lead: cards of same value (or all 7s)."""
        non_seven_values = {c.value for c in move.cards if c.value != "7"}
        return len(non_seven_values) <= 1
    
    def is_legal_response(self, move: Move, lead_move: Move, player: str) -> bool:
        """Valid response: match lead or play lowest cards."""
        lead_value = lead_move[0].int_value
        if lead_value == 7:
            lead_value = 14
        
        hand_sorted = sorted(
            self.state.players_hands[player],
            key=lambda c: c.int_value
        )
        
        move_values = [c.int_value for c in move.cards]
        low_cards = [v for v in move_values if v < lead_value]
        
        allowed_low = hand_sorted[:len(low_cards)]
        
        for card in move.cards:
            if card.int_value == 7:
                continue
            if card.int_value >= lead_value:
                continue
            if card not in allowed_low:
                return False
        
        if len(move) != len(lead_move):
            return False
        
        return True
    
    def is_legal_move(self, player: str, move: Move) -> bool:
        """Check move legality."""
        # Must own cards
        if not all(c in self.state.players_hands[player] for c in move.cards):
            return False
        
        if self.state.current_round.starting_player == player:
            return self.is_legal_lead(move)
        else:
            lead_move = self.state.current_round.turns[0].move
            return self.is_legal_response(move, lead_move, player)
    
    def legal_moveset(self, player: str) -> set:
        """Generate all legal moves for player."""
        legal_moves = set()
        hand = self.state.players_hands[player]
        
        for num_cards in range(1, len(hand) + 1):
            for combo in combinations(hand, num_cards):
                move = Move(list(combo))
                if self.is_legal_move(player, move):
                    legal_moves.add(move)
        
        return legal_moves
    
    def _return_starting_player(self, turns: list[TurnRecord]) -> str:
        """Determine next round's starting player (previous winner)."""
        best_player = None
        best_value = -1
        
        for turn in turns:
            value = turn.move[0].int_value
            if value >= best_value:
                best_player = turn.player
                best_value = value
        
        return best_player
    
    def _check_deck(self, amount: int) -> bool:
        """Check if deck has enough cards."""
        return amount <= len(self.state.deck)
