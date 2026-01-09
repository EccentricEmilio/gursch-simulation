from terminal_ui import TerminalUI
from state import GameState
from engine import GameEngine
from models import RandomPolicy
import pydealer
from simulation import Simulation
from constants import *
import numpy as np
from pprint import pprint

player_count = 4
settings = {}
random_policies = [RandomPolicy()] * player_count

default_sim = Simulation(random_policies)
score_list = []

if __name__ == "__main__":
    result = default_sim.run_terminal_sim(player_count)
    print("----------SIM DONE----------")
    print("Players:", result.players)
    print("Policies:", result.policies)
    print("Loser Score:", result.loser_score)
    print("Ties:", result.ties)
    #print("Board:")
    #pprint(result.board)