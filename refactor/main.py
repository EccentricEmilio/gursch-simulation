from terminal_ui import TerminalUI
from state import GameState
from engine import GameEngine
from models import RandomPolicy, HighestPolicy
import pydealer
from simulation import Simulation
from constants import *
import numpy as np
from pprint import pprint

player_count = 4
settings = {}
highest_policies = [HighestPolicy()] * player_count
random_policies = [RandomPolicy()] * player_count

default_sim = Simulation(highest_policies)
score_list = []

if __name__ == "__main__":
    mean = default_sim.run_terminal_sim(player_count)
    
    result = default_sim.run_terminal_sim(player_count)
    print("----------SIM DONE----------")
    print("Players:", result.players)
    print("Policies:", result.policies)
    print("Loser(s): ", result.losers)
    print("Loser Score:", result.highest_score)
    