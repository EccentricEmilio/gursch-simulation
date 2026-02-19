"""Game constants for Gursch card game."""

# Game phases
SETUP_PHASE = 0
THROW_PHASE = 1
PLAY_PHASE = 2
GAMEOVER_PHASE = 3

PHASES = {
    "0": "Setup phase",
    "1": "Throw phase",
    "2": "Play phase",
    "3": "Game is over",
}

# Card value mapping from pydealer to abbreviations
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

# Poker card values for comparison
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

# Default game settings
DEFAULT_SETTINGS = {
    "hand_size": 5,
    "response_requires_duplicates": False,
    "joker_amount_in_deck": 0,
}

# Player names
PLAYER_NAMES = [
    "Amanda",
    "Bertil",
    "Carina",
    "Daniel",
    "Elinor",
    "Fabian" 
]
