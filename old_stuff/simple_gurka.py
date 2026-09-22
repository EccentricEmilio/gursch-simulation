import random


# Card values:
# 2 = lowest, A = highest
RANKS = list(range(2, 11)) + ["J", "Q", "K", "A"]
VALUES = {rank: i for i, rank in enumerate(RANKS, start=2)}


def create_deck():
    """Create and shuffle a standard 52-card deck."""
    suits = ["H", "D", "C", "S"]
    deck = [(rank, suit) for rank in RANKS for suit in suits]
    random.shuffle(deck)
    return deck


def card_value(card):
    """Return the numerical value of a card."""
    return VALUES[card[0]]


def card_string(card):
    """Convert a card tuple to a readable string."""
    return f"{card[0]}{card[1]}"


def lowest_card(hand):
    """Return the lowest-valued card in a hand."""
    return min(hand, key=card_value)


def highest_card(hand):
    """Return the highest-valued card in a hand."""
    return max(hand, key=card_value)


def choose_card(hand, current_card):
    """
    Basic strategy:

    If this is the first card of a round:
        Play the highest card.

    Otherwise:
        Play the lowest card that is higher than the current card.
        If none exists, play the lowest card.
    """
    if current_card is None:
        return highest_card(hand)

    higher_cards = [
        card for card in hand
        if card_value(card) > card_value(current_card)
    ]

    if higher_cards:
        return min(higher_cards, key=card_value)

    return lowest_card(hand)


class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []

    def draw_card(self, card):
        self.hand.append(card)

    def play_card(self, card):
        self.hand.remove(card)
        return card

    def show_hand(self):
        return " ".join(card_string(card) for card in sorted(
            self.hand, key=card_value
        ))

    def lowest_value(self):
        return min(card_value(card) for card in self.hand)


def play_round(players, starting_player):
    """
    Play one normal round.

    The starting player chooses any card.
    Every other player:
      - plays the lowest card higher than the current card
      - otherwise plays their lowest card

    If an Ace is played, everyone else must play their lowest card.
    Multiple Aces cannot be played in the same round because after
    an Ace, all other players are forced to play their lowest card.
    """

    print("\n" + "=" * 60)
    print("NEW ROUND")
    print("=" * 60)

    played_cards = []

    current_card = None
    highest_card_played = None
    winner = None

    for i in range(len(players)):
        player_index = (starting_player + i) % len(players)
        player = players[player_index]

        # First player can choose freely.
        if i == 0:
            card = choose_card(player.hand, None)

        # If an Ace was played, everyone else must play their lowest card.
        elif card_value(current_card) == VALUES["A"]:
            card = lowest_card(player.hand)

        else:
            card = choose_card(player.hand, current_card)

        player.play_card(card)

        played_cards.append((player, card))
        current_card = card

        print(
            f"{player.name:10} plays {card_string(card):>3} "
            f"(hand: {player.show_hand()})"
        )

        # Track highest card.
        if highest_card_played is None or card_value(card) > card_value(
            highest_card_played
        ):
            highest_card_played = card
            winner = player

    print("-" * 60)

    print(
        f"{winner.name} wins the round with "
        f"{card_string(highest_card_played)}"
    )

    # The winner starts the next round.
    return players.index(winner)


def play_final_round(players, starting_player):
    """
    Final round.

    The player who won the previous round starts by playing
    their final card.

    Everyone else then plays their final card.

    The LOWEST card wins the game.
    """

    print("\n" + "=" * 60)
    print("FINAL ROUND")
    print("=" * 60)

    played_cards = []

    for i in range(len(players)):
        player_index = (starting_player + i) % len(players)
        player = players[player_index]

        card = player.hand[0]
        player.play_card(card)

        played_cards.append((player, card))

        print(f"{player.name:10} plays {card_string(card):>3}")

    winner, winning_card = min(
        played_cards,
        key=lambda x: card_value(x[1])
    )

    print("-" * 60)
    print(
        f"{winner.name} WINS THE GAME with "
        f"{card_string(winning_card)}!"
    )

    return winner


def deal(players):
    """Deal 7 cards to each player."""
    deck = create_deck()

    for _ in range(7):
        for player in players:
            player.draw_card(deck.pop())

    return deck


def print_hands(players):
    print("\nStarting hands:")
    for player in players:
        print(f"{player.name:10}: {player.show_hand()}")


def play_game(num_players=4):
    """
    Simulate one complete game of Gurka.
    """

    players = [
        Player(f"Player {i + 1}")
        for i in range(num_players)
    ]

    deal(players)

    print_hands(players)

    # Player to the left of the dealer starts.
    # We simply use Player 1 as the first player.
    starting_player = 0

    # Each normal round removes one card from every hand.
    # With 7 cards, there are 6 normal rounds.
    while len(players[0].hand) > 1:

        starting_player = play_round(
            players,
            starting_player
        )

        print("\nCards remaining:")
        for player in players:
            print(
                f"{player.name:10}: "
                f"{player.show_hand()}"
            )

    # Final round
    return play_final_round(
        players,
        starting_player
    )


def main():
    print("=" * 60)
    print("GURKA - TERMINAL SIMULATOR")
    print("=" * 60)

    while True:
        try:
            num_players = int(
                input("\nNumber of players (2-8): ")
            )

            if 2 <= num_players <= 8:
                break

            print("Please enter a number between 2 and 8.")

        except ValueError:
            print("Please enter a valid number.")

    play_game(num_players)


if __name__ == "__main__":
    main()