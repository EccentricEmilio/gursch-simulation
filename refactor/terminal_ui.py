from state import Card, GameState, RoundRecord
from constants import *
class TerminalUI:
    def __init__(self, state):
        self.state = state
        
        pass 
    
    def print_sim(self):
        board = self.state.board
        
            
        for round in board:
            print(DIVIDER)
            for p, h in round.players_hands.items():
                self.print_hand(f"{p}'s hand:", h)
            print(DIVIDER)
            print("Turn:", round.index)
            print("Phase:", PHASES[str(round.game_phase)])
            self.print_round(round)            
        self.print_loser()
        
    def print_round(self, round):
        if round.type == "throw":
            self.print_throw_round(round)
        elif round.type == "play":
            self.print_play_round(round)

    
    def print_throw_round(self, round: RoundRecord):
        throw_num = round.get_lowest_throw_num()
        for throw in round.turns:
            print(f"Player {throw.player} wants to throw {throw.throw_count} cards.")
        if round.turns[0].thrown_cards != []:
            print(f"{throw_num} cards thrown.")
            for throw in round.turns:
                print(f"Player {throw.player} throws these cards: {throw.thrown_cards}")
                #print(f"Player {throw.player0} gets these cards back:")
        else:
            print("None cards thrown.")
            print("Play phase initiated.")
            
            
    def print_play_round(self, round: RoundRecord):
        print(round.starting_player + " is starting player.")
        for turn_record in round.turns:
            print(turn_record.player + " has played this move:", turn_record.move)
        
    
    def print_setup(self):
        print("Initial game setup complete.")
        print("The starting player is:", self.state.player_zero)
        
    
    def print_game_state(self):
        print("------------------------")
        print("------------------------")
        
        print("Turn: " + str(self.state.round_index))
        print("Gamephase: " + PHASES[str(self.state.phase)])
        print("Hands:")
        for player in self.state.players:
            self.print_hand(str(player)+"'s hand:", player)
            
        print("------------------------")
        print("------------------------")

    def print_hand(self, prefix: str, hand: list):
        message = [prefix]
        for card in hand:
            message.append(str(card))
        print(" ".join(message))


    def print_loser(self):
        print("Game is over")
        if len(self.state.losers) == 1:
            print(self.state.losers[0] + " lost, with a score of " + str(self.state.highest_score))
        else:
            print("It's a tie!")
            print("These players tied: " + str(self.state.losers))