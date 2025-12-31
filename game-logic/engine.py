from constants import *
from state import GameState
  
class GameEngine:
    def __init__(self, state: GameState):
        self.state = state

    def process_turn(self, prompt_player: callable):
        self.state.current_round = {}
        
        last_player_index = self.state.starting_player_index - 1
        if last_player_index < 0:
            last_player_index = len(self.state.players) - 1
        
        self.state.active_player_index = self.state.starting_player_index
        while not self.state.active_player_index == last_player_index:
            active_player = self.state.players[self.state.active_player_index]

            chosen_cards = prompt_player(active_player, self.state.players_hands[active_player], self.validate_player_input)
            # Normalize
            chosen_cards = [c.upper() for c in chosen_cards]
            self.state.current_round[active_player] = chosen_cards
            for card in chosen_cards:
                self.state.players_hands[active_player].remove(card)

            # Shift active player
            self.state.active_player_index += 1
            if self.state.active_player_index >= len(self.state.players):
                self.state.active_player_index = 0

    def validate_player_input(self, player, chosen_cards):
        # normalize
        chosen_cards = [c.upper() for c in chosen_cards]
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
            return False, ERROR_MESSAGES["no_cards"]
        if any(c not in hand for c in chosen_cards):
            return False, ERROR_MESSAGES["invalid_card"]
        if len(chosen_cards) != len(set(chosen_cards)):
            return False, ERROR_MESSAGES["duplicate_cards"]
        if not currently_starter:
            if len(chosen_cards) != len(self.state.current_round[starting_player]):
                return False, ERROR_MESSAGES["mismatched_count"]
        
        values = [POKER_VALUES[c[0]] for c in chosen_cards]
        if currently_starter:
            if len(set(values)) != 1:
                return False, ERROR_MESSAGES["different_values"]
        if not currently_starter:
            starting_values = [POKER_VALUES[c[0]] for c in starting_players_cards]
            if NORMAL_SETTINGS["response_requires_duplicates"]:
                if values.count(values[0]) < starting_values.count(starting_values[0]):
                    return False, ERROR_MESSAGES["different_values"]
                
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
                    return False, ERROR_MESSAGES["disallowed_value"]
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
                card = hand[-1]
                value = card[0]
                rank_value = POKER_VALUES.get(value)

                if rank_value >= winner_value:
                    winner = p
                    winner_value = rank_value

        # This block currently only handles the last card played in the round
        if self.state.turn_index > 0:
            for player, cards in self.state.current_round.items():
                card = cards[-1]
                value = card[0]
                rank_value = POKER_VALUES.get(value)

                if rank_value >= winner_value:
                    winner = player
                    winner_value = rank_value
        
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
            self.state.game_is_over = True
        
            player_scores = []
            for player, cards in self.state.current_round.items():
                values = [POKER_VALUES[c[0]] for c in cards]
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