"""
Times gursh.minmax.choose_move_maxn across a grid of settings.

Usage:
    python benchmark.py
    python benchmark.py --players 3 4 --hands 3 4 5 --sims 10 50 --trials 5
    python benchmark.py --budget 10      # skip a config if one call exceeds 10 s

maxn has no pruning, so cost grows very fast with hand_size and player_count.
Start small and work up. The --budget flag stops a config early (and skips
larger hand sizes for the same player_count / sims) once a single call is too slow.
"""
import argparse
import random
import statistics
import time

from gursh import state as gu_state, minmax as gu_minmax, mcts as gu_mcts


def time_one(player_count: int, hand_size: int, simulations: int, model: int) -> float:
    """Time a single choose_move_maxn call on a fresh lead state."""
    state = gu_state.create_new_state(player_count=player_count, hand_size=hand_size)
    start = time.perf_counter()
    if model == 1:
        gu_minmax.choose_move_maxn(state, simulations=simulations)
    elif model == 2:
        gu_mcts.choose_move_mcts(state, iterations=simulations)
        pass
    else:
        raise ValueError(f"Unknown model: {model}")
    return time.perf_counter() - start


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=int, nargs="+", default=[1, 2], help="1=MaxN, 2=MCTS")
    parser.add_argument("--players", type=int, nargs="+", default=[2, 3])
    parser.add_argument("--hands", type=int, nargs="+", default=[2, 3, 4])
    parser.add_argument("--sims", type=int, nargs="+", default=[10, 50])
    parser.add_argument("--trials", type=int, default=5, help="timed calls per config")
    parser.add_argument("--budget", type=float, default=30.0,
                        help="seconds; if one call exceeds this, skip bigger hand sizes")
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    random.seed(args.seed)

    header = f"{'players':>7} {'hand':>5} {'sims':>5} | {'mean s':>9} {'median s':>9} {'min s':>9} {'max s':>9} | {'ms/sim':>9} {'model':>5}"
    print(header)
    print("-" * len(header))

    for model in args.model:
        for players in args.players:
            for sims in args.sims:
                for hand in sorted(args.hands):
                    times = []
                    for _ in range(args.trials):
                        t = time_one(players, hand, sims, model)
                        times.append(t)
                        if t > args.budget:
                            break

                    mean = statistics.mean(times)
                    print(f"{players:>7} {hand:>5} {sims:>5} | "
                          f"{mean:>9.4f} {statistics.median(times):>9.4f} "
                          f"{min(times):>9.4f} {max(times):>9.4f} | "
                          f"{mean / sims * 1000:>9.3f} {model:>5}")

                    if max(times) > args.budget:
                        print(f"        (over {args.budget}s budget; skipping larger hands "
                              f"for players={players}, sims={sims})")
                        break


if __name__ == "__main__":
    main()
