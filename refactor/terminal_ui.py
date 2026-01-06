from state import Card, GameState
class TerminalUI:
    def __init__(self):
        pass 
        
    def print_game_state(self, turn_index: int, players_hand: dict, starting_player:str):
        players = list(players_hand.keys())
        print("------------------------")
        print("------------------------")
        print("Turn: " + str(turn_index))
        print("Hands:")
        
        for player in players:
            self.print_hand(str(player)+ "'s hand:", players_hand[player])

        if turn_index == 0:
            print("Initial game setup complete.")
            self.print_starting_player(starting_player)
                    # Prints should be handled outside engine
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
    
    def print_starting_player(self, player: str):
        print("The starting player is:", player)
    
    def print_loser(self, loser_score: tuple, ties: list):
        if ties == []:
            loser = loser_score[0]
            score = loser_score[1]
            print("Game is over")
            print(loser + " lost, with a score of " + str(score))
        elif ties != []:
            print("It's a tie!")
            print("These players tied: " + str(ties))