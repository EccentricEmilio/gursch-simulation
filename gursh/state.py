from dataclasses import dataclass
from random import shuffle

'''
state = fox.GameState.new_game()
engine = fox.GameEngine()

while not state.is_game_over():
    legal_actions = engine.get_legal_actions(state)

    action = random.choice(legal_actions)
    engine.apply_action(state, action)
'''

#TODO Implement copy function for State to make faster copying possible
@dataclass
class State:
    hands: list[list[int]]
    hand_info: list[set]
    current_player: int # index of hands

    highest_value: int | None # value to match
    round_leader: int | None # Eventual round winner

    played_this_round: int # amount of cards that has been played this round
    played_cards: list[int] # cards that have been played


    @classmethod
    def new_game(cls, hands: list = [], player_count: int = 2, hand_size: int = 3):
        deck = list(range(2, 15)) * 4
        shuffle(deck)

        if hands == []:
            hands = [
                deck[i * hand_size:(i + 1) * hand_size]
                for i in range(player_count)
            ]

        hand_info = [
            set(range(2, 15))
            for _ in range(player_count)
        ]

        return cls(
            hands=hands,
            hand_info=hand_info,
            current_player=0,
            highest_value=None,
            round_leader=None,
            played_this_round=0,
            played_cards=[],
        )


    def __str__(self):
        return (
            f"hands={self.hands}\n"
            f"current_player={self.current_player}\n"
            f"highest_value={self.highest_value}\n"
            f"round_winner={self.round_leader}\n"
            f"played_this_round={self.played_this_round}\n"
            f"played_cards={self.played_cards}\n"
            f"hand_info={self.hand_info}"
        )