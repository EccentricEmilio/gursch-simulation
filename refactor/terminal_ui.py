from state import Card, GameState
class TerminalUI:
    def __init__(self):
        pass 
        
    def print_game_state(self, state: GameState):
    #def print_game_state(self, turn_index: int, players_hand: dict, starting_player:str):
        print("------------------------")
        print("------------------------")
        print("Turn: " + str(state.turn_index))
        print("Hands:")
        
        for player in state.players:
            self.print_hand(str(player)+ "'s hand:", state.players_hands[player])

        if state.turn_index == 0:
            starting_player = state.players[state.starting_player_index]
            print("Initial game setup complete.")
            print("The starting player is:", starting_player)
        #print("Round " + str(self.state.turn_index) + " winner is " + self.state.players[self.state.starting_player_index])
        #print("Current round results:" + str(self.state.current_round))
        print("------------------------")
        print("------------------------")

    def print_hand(self, prefix: str, hand: list):
        message = [prefix]
        for card in hand:
            message.append(card.raw)
        print(" ".join(message))

    def print_players_choice(self, state):
        players_order = state.players[state.active_player_index:]
        players_order.extend(state.players[:state.active_player_index])
        for player in players_order:
            chosen_cards = state.current_round[player]
            self.print_hand(player + " have chosen these cards:", chosen_cards)
    
    def print_loser(self, loser_score: tuple, ties: list):
        if ties == []:
            loser = loser_score[0]
            score = loser_score[1]
            print("Game is over")
            print(loser + " lost, with a score of " + str(score))
        elif ties != []:
            print("It's a tie!")
            print("These players tied: " + str(ties))