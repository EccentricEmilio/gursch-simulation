VALUE_MAP = {
    "2": "2",
    "3": "3",
    "4": "4",
    "5": "5",
    "6": "6",
    "7": "7",
    "8": "8",
    "9": "9",
    "10": "T",
    "Jack": "J",
    "Queen": "Q",
    "King": "K",
    "Ace": "A"
}

POKER_VALUES = {
    "A": 14,
    "K": 13,
    "Q": 12,
    "J": 11,
    "T": 10,
    "9": 9,
    "8": 8,
    "7": 7,
    "6": 6,
    "5": 5,
    "4": 4,
    "3": 3,
    "2": 2,
}

ERROR_MESSAGES = {
            "no_cards": "No cards chosen.",
            "invalid_card": "Invalid card chosen.",
            "duplicate_cards": "Duplicate cards chosen.",
            "different_values": "All chosen cards must be of the same value.",
            "mismatched_count": "You must play the same number of cards as player-1.",
            "disallowed_value": "Value must either be your lowest available or match starting_player."
        }

CUSTOM_RULES = {
    "cards_per_hand": 5,
    "deck_type": "standard",
    "player_count": 2,
    # If this is checked, responses must include duplicate cards or all cards must be the players
    # individual lowest cards. For example, if player-1 plays two Queens, player-2 must also play atleast
    # two Queens if they have them, otherwise they must play two of their lowest cards.
    "response_requires_duplicates": False,
    # Jokers can be used as wild cards, the act the same as sevens.
    "joker_amount_in_deck": 0,
}

PLAYER_NAMES = [
    "Abraham",
    "Benjamin",
    "Caleb",
    "Daniel",
    "Emil",
    "Fred"
]

PLAYERS_HANDS_DEBUG = {
    "Abraham": ["2H", "2S", "6S", "8H", "KC"],
    "Benjamin": ["2H", "2S", "6S", "8H", "KC"],
    #"Caleb": ["2C", "JC", "KD", "KS", "QC"],
    #"Daniel": ["2S", "5H", "AS", "JD", "QH"]
}

def abbreviate(self):
    v = VALUE_MAP[self.value]
    abbreviation = v + self.suit[0]
    return abbreviation   