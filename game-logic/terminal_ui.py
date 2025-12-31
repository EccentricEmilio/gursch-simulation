class TerminalUI:
    def __init__(self):
        pass 
        
    def print_game_state(self, turn_index: int, players_hand: dict, 
                         initial_setup: bool = False, starting_player: str = ""):
        players = list(players_hand.keys())
        print("------------------------")
        print("------------------------")
        print("Turn: " + str(turn_index))
        print("Hands:")
        
        for player in players:
            self.print_hand(str(player)+ "'s hand:", players_hand[player])
        
        if initial_setup:
            print("Initial game setup complete.")
            self.print_starting_player(starting_player)
        print("------------------------")
        print("------------------------")

    def print_hand(self, prefix: str, hand: list):
        message = [prefix]
        for card in hand:
            message.append(card)
        print(" ".join(message))

    def prompt_player(self, player: str, hand: list, validate_player_input: function):
            print("It's " + player + "'s turn.")
            self.print_hand("This is your hand:", hand)
            chosen_cards = input("Choose which cards to play: ")
            chosen_cards = chosen_cards.split()

            valid, err = validate_player_input(player, chosen_cards)
            if not valid:
                print(err)
                return self.prompt_player(player, hand, validate_player_input)

            self.print_hand("You have chosen these cards:", chosen_cards)
            return chosen_cards
    
    def print_starting_player(self, player: str):
        print("The starting player is:", player)
    
    def print_loser(self, loser_score: tuple, ties):
        if ties == []:
            loser = loser_score[0]
            score = loser_score[1]
            print("Game is over")
            print(loser + " lost, with a score of " + str(score))
        elif ties != []:
            print("It's a tie!")
            print("These players tied: " + str(ties))