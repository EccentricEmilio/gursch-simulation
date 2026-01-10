from terminal_ui import TerminalUI
from state import GameState, Card
from engine import GameEngine
from models import RandomPolicy
import pydealer
from simulation import Simulation
from constants import *
import numpy as np
from pprint import pprint

#PLAYERS_HANDS_DEBUG = {
#    "Abraham" : [Card("2" "H"), Card("6","S"), Card("8","S"), Card("K","H"), Card("J","C")],
#}
PLAYERS_HANDS_DEBUG = [
    Card("2","H"), 
    Card("6","S"), 
    Card("8","S"), 
    Card("K","H"), 
    Card("J","C")
]


def debug(self, player_count: int = 3):
    state = GameState(player_count, self.settings)
    engine = GameEngine(state, self.policies)
    
    hand = PLAYERS_HANDS_DEBUG
    
    engine.swap_hand("Amanda")
    print(state.players_hands)
    hand = state.players_hands["Amanda"]
    new_cards = hand[:3]
    engine.swap_cards(new_cards, "Amanda")
    print(state.players_hands)
    '''
    state.deal_initial_hands()
    engine.determine_starting_index()
    while state.phase == 0:
        engine.process_turn() 
        engine.resolve_round() # determine round winner and update state
        engine.advance_state() # Check if game is over
    return self.to_result(state)      
    '''

player_count = 4
settings = {}
random_policies = [RandomPolicy()] * player_count

sim = Simulation(random_policies)
Simulation.debug = debug

score_list = []

if __name__ == "__main__":
    sim.debug()