"""Main entry point for Gursch game."""

from models import RandomPolicy, HighestPolicy
from simulation import Simulation

if __name__ == "__main__":
    player_count = 4
    policies = [HighestPolicy()] * player_count
    
    print("Starting simulation...")
    sim = Simulation(policies)
    terminal_sim = True
    if terminal_sim:
        result = sim.run_terminal_sim(player_count)
    else:

        result = sim.run_sim(player_count)

        print("=" * 40)
        print("GAME COMPLETE")
        print("=" * 40)
        print(f"Players: {result.players}")
        print(f"Policies: {result.policies}")
        print(f"Losers: {result.losers}")
        print(f"Score: {result.highest_score}")
        print(f"Total rounds: {len(result.board)}")
