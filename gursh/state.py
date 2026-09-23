from dataclasses import dataclass, field
from random import shuffle
from typing import cast


@dataclass
class ObservableState:
    hands: list[list[int] | list[None]] # same shape/indexing as State.hands: one
                                   # list per player, in the SAME index. The
                                   # viewer's own hand (hands[viewer]) holds
                                   # real ints. Every other hand holds None
                                   # in place of each hidden card - length
                                   # still matches the real hand size, since
                                   # you can see how many cards someone has
                                   # even if you can't see which ones. This
                                   # also leaves room to later reveal a
                                   # SPECIFIC opponent card (swap one None
                                   # for a real int) without changing shape.
    hand_info: list[set]
    viewer: int # index of hands whose observation this is (own_hand's index)
    current_player: int # index of hands whose TURN it is - not necessarily
                         # the same as viewer; this state might be built to
                         # show a non-mover their own view mid someone
                         # else's turn

    highest_value: int # value to match
    round_leader: int # Eventual round winner

    played_this_round: int # amount of cards that has been played this round
    played_cards: list[int] # cards that have been played

    @property
    def own_hand(self) -> list[int]:
        '''
        The viewer's own hand as a plain list[int] - never contains None,
        so any function that only expects int-based hand methods (max(),
        sums, membership checks, etc.) can call this directly, exactly as
        it would on State.hands[player].

        hands is typed list[list[int | None]] since OTHER players' hands
        legitimately can hold None, so the type checker can't statically
        know this particular slot never does - the assert enforces that
        invariant at runtime, and the cast tells the type checker to trust
        it afterward, rather than silently swallowing a bug by e.g.
        filtering out unexpected Nones.
        '''
        hand = self.hands[self.viewer]
        assert all(card is not None for card in hand), (
            f"viewer {self.viewer}'s own hand contains None: {hand}"
        )
        return cast(list[int], hand)


#TODO Implement copy function for State to make faster copying possible
@dataclass
class State:
    hands: list[list[int]]
    hand_info: list[set]
    current_player: int # index of hands

    played_this_round: int = 0 # amount of cards that has been played this round
    played_cards: list[int] = field(default_factory=list)  # cards that have been played

    highest_value: int = -1 # value to match
    round_leader: int = -1 # Eventual round winner

    def copy(self) -> "State":
        return State(
            hands=[hand[:] for hand in self.hands],
            hand_info=[info.copy() for info in self.hand_info],
            current_player=self.current_player,
            played_this_round=self.played_this_round,
            played_cards=self.played_cards[:],
            highest_value=self.highest_value,
            round_leader=self.round_leader,
        )

    def __str__(self):
        return (
            f"hands={self.hands}\n"
            f"current_player={self.current_player}\n"
            f"highest_value={self.highest_value}\n"
            f"round_leader={self.round_leader}\n"
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

    def get_utilities(self) -> list[float]:
        '''
        Assumes is_game_over == True. Returns one utility value per player
        (length == player_count).

        Payment model: whoever holds the highest final card (value V) is the
        loser ("gurka") and pays V to every other player. If k players tie
        for the highest card, they share that cost evenly: each winner still
        receives the same total V (not k*V), but each of the k tied losers
        only pays V/k to each winner, rather than each paying the full V.
        If every player ties (k == n, no winners), no payment occurs and
        every utility is 0.0. This is a zero-sum transfer either way:
        sum(get_utilities()) == 0.0 always, which is a good sanity check.
        '''
        final_cards = [hand[0] for hand in self.hands]
        max_value = max(final_cards)
        n = len(final_cards)

        losers = [i for i in range(n) if final_cards[i] == max_value]
        k = len(losers)
        winners_count = n - k

        utilities = [0.0] * n
        if winners_count == 0:
            # Everyone tied - no winners to pay, nothing changes hands.
            return utilities

        share_per_loser = max_value / k
        for i in range(n):
            if i in losers:
                utilities[i] = -share_per_loser * winners_count
            else:
                utilities[i] = max_value

        return utilities

                
    def get_observable_state(self, viewer: int) -> ObservableState:
        hands = [
            list(hand) if i == viewer else [None] * len(hand)
            for i, hand in enumerate(self.hands)
        ]

        obs_state = ObservableState(
            hands=hands,
            hand_info=self.hand_info,
            viewer=viewer,
            current_player=self.current_player,
            highest_value=self.highest_value,
            round_leader=self.round_leader,
            played_this_round=self.played_this_round,
            played_cards=self.played_cards
        )

        return obs_state


def create_new_state(hands: list = [], player_count: int = 2, hand_size: int = 3):
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

    return State(
        hands=hands,
        hand_info=hand_info,
        current_player=0,
        highest_value=-1,
        round_leader=-1,
        played_this_round=0,
        played_cards=[],
    )


def state_from_observable(obs: "ObservableState") -> "State":
    '''
    Reconstruct a full State from what a single player (obs.viewer) can
    actually see, for feeding into determinize_state / choose_move_maxn.
    Each card that's None (hidden) becomes a -1 sentinel placeholder;
    any card that's already a real int (obs.viewer's own hand, and any
    future partially-revealed opponent card) passes through unchanged.
    determinize_state only ever reads len(state.hands[i]) for i !=
    self_index before overwriting that hand completely with sampled
    cards, so the -1 placeholders themselves are never read for their
    value - only their count matters.
    '''
    hands = [
        [-1 if card is None else card for card in hand]
        for hand in obs.hands
    ]

    return State(
        hands=hands,
        hand_info=[set(s) for s in obs.hand_info],
        current_player=obs.current_player,
        played_this_round=obs.played_this_round,
        played_cards=list(obs.played_cards),
        highest_value=obs.highest_value,
        round_leader=obs.round_leader,
    )