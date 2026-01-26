from terminal_ui import TerminalUI
from state import GameState
from engine import GameEngine
from models import RandomPolicy, HighestPolicy
import pydealer
from simulation import Simulation
from constants import *
import numpy as np
from pprint import pprint

player_count = 6
settings = {}
highest_policies = [HighestPolicy()] * player_count
random_policies = [RandomPolicy()] * player_count
custom_policies = [HighestPolicy(), RandomPolicy()]

sim = Simulation(highest_policies)
score_list = []

if __name__ == "__main__":
    results = sim.run_several_sim(10000, player_count)
    scores = []
    for game in results:
        scores.append(game.highest_score)
    scores = np.array(scores)
    scores_mean = np.mean(scores)
    print("Policies: ", results[0].policies)
    print("Mean: ", scores_mean)
    