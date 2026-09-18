from dataclasses import dataclass, field
from random import shuffle


@dataclass
class ObservableState:
    own_hand: list[int]
    hand_info: list[set]
    current_player: int # index of hands

    highest_value: int | None # value to match
    round_leader: int | None # Eventual round winner

    played_this_round: int # amount of cards that has been played this round
    played_cards: list[int] # cards that have been played


#TODO Implement copy function for State to make faster copying possible
@dataclass
class State:
    hands: list[list[int]]
    hand_info: list[set]
    current_player: int # index of hands

    played_this_round: int = 0 # amount of cards that has been played this round
    played_cards: list[int] = field(default_factory=list)  # cards that have been played

    highest_value: int | None = None # value to match
    round_leader: int | None = None # Eventual round winner
    winner: int | None = None


    @classmethod
    def create_new_game(cls, hands: list = [], player_count: int = 2, hand_size: int = 3):
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

    def is_game_over(self) -> bool:
        '''
        Check if the state is over
        Terminal means that every person has 1 card left, no actions left to be made
        '''
        return all(len(hand) == 1 for hand in self.hands)

    def get_winner(self) -> float:
        '''
        Assumes is_game_over == True and returns 1 for player_0 win
        '''
        flat_hands = [hand[0] for hand in self.hands]
        max_value = max(flat_hands)

        if flat_hands[0] == max_value:
            if flat_hands[1] == max_value:
                return 0.5
            else:
                return 0.0
        else:
            return 1.0

                
    def get_observable_state(self, player):
        obs_state = ObservableState(
            own_hand=self.hands[player],
            hand_info=self.hand_info,
            current_player=self.current_player,
            highest_value=self.highest_value,
            round_leader=self.round_leader,
            played_this_round=self.played_this_round,
            played_cards=self.played_cards
        )

        return obs_state