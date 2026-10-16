"""
Tournament runner for gursh.

Examples
--------
    # Default: HighestCardAgent vs MixedMaxNMCTS, 50 games
    python tournament.py

    # Pick agents (with optional parameters) and number of games
    python tournament.py -a highest mixed:maxn=200,mcts=2000,limit=4 -n 500

    # Three players, 5 cards each, 8 worker processes, reproducible
    python tournament.py -a random highest mcts:iters=1000 --hand-size 5 -j 8 --seed 42

    # Save per-game results and a JSON summary
    python tournament.py -n 200 --csv games.csv --json summary.json

Agent spec format:  name[:key=value,key=value]
    highest
    random
    maxn   : sims=<int>
    mcts   : iters=<int>, c=<float>
    mixed  : maxn=<int>, mcts=<int>, c=<float>, limit=<int>

Seat rotation (on by default) shifts which agent sits in which seat every game,
so that no agent benefits from always being the first to lead. Use
--no-rotate to keep agents in fixed seats.
"""
import argparse
import csv
import json
import math
import multiprocessing as mp
import os
import random
import statistics
import sys
import time
from typing import Any, Sequence

import gursh as gu


# ---------------------------------------------------------------------------
# Agent registry
# ---------------------------------------------------------------------------

# name -> (class, {cli_key: (constructor_kwarg, type)})
AGENT_TYPES: dict[str, tuple[type, dict[str, tuple[str, type]]]] = {
    "highest": (gu.agents.HighestCardAgent, {}),
    "random": (gu.agents.RandomAgent, {}),
    "maxn": (gu.agents.MaxNAgent, {"sims": ("simulations", int)}),
    "mcts": (gu.agents.MCTSAgent, {"iters": ("iterations", int), "c": ("c", float)}),
    "mixed": (
        gu.agents.MixedMaxNMCTS,
        {
            "maxn": ("maxN_iterations", int),
            "mcts": ("mcts_iterations", int),
            "c": ("c", float),
            "limit": ("size_limit", int),
        },
    ),
}


def build_agent(spec: str) -> gu.agents.Agent:
    """Turn a spec string like 'mixed:maxn=200,mcts=2000' into an Agent."""
    name, _, argstr = spec.partition(":")
    name = name.strip().lower()
    if name not in AGENT_TYPES:
        raise ValueError(f"unknown agent '{name}'. Choose from: {', '.join(AGENT_TYPES)}")
    cls, params = AGENT_TYPES[name]

    kwargs: dict[str, Any] = {}
    if argstr:
        for item in argstr.split(","):
            key, sep, val = item.partition("=")
            key = key.strip()
            if not sep:
                raise ValueError(f"bad parameter '{item}' in '{spec}' (expected key=value)")
            if key not in params:
                valid = ", ".join(params) or "none"
                raise ValueError(f"agent '{name}' has no parameter '{key}' (valid: {valid})")
            kwarg_name, caster = params[key]
            kwargs[kwarg_name] = caster(val)
    return cls(**kwargs)


def agent_spec(spec: str) -> str:
    """argparse type: validate the spec early, keep it as a string (picklable)."""
    try:
        build_agent(spec)
    except (ValueError, TypeError) as e:
        raise argparse.ArgumentTypeError(str(e))
    return spec


def unique_labels(specs: list[str]) -> list[str]:
    """Label agents by spec; disambiguate duplicates as 'spec#1', 'spec#2'."""
    labels = []
    for i, spec in enumerate(specs):
        if specs.count(spec) > 1:
            labels.append(f"{spec}#{specs[:i + 1].count(spec)}")
        else:
            labels.append(spec)
    return labels


# ---------------------------------------------------------------------------
# Running games
# ---------------------------------------------------------------------------

def run_game(job: tuple) -> dict[str, Any]:
    """
    Play one full game. Top-level function so it can be used by multiprocessing.

    Returns utilities indexed by AGENT (not by seat), wall time for the game,
    number of moves, and the decision time of every move per agent.
    """
    game_idx, seed, specs, hand_size, rotate, verbose = job

    random.seed(seed)
    agents = [build_agent(s) for s in specs]
    n = len(agents)

    # seat_to_agent[seat] = index of the agent sitting in that seat
    shift = game_idx % n if rotate else 0
    seat_to_agent = [(seat + shift) % n for seat in range(n)]

    state = gu.state.create_new_state(player_count=n, hand_size=hand_size)
    if verbose:
        print(f"--- game {game_idx} (seed {seed}, shift {shift}) ---")
        print(state)

    move_times: list[list[float]] = [[] for _ in range(n)]
    moves = 0
    game_start = time.perf_counter()

    while not state.is_game_over():
        seat = state.current_player
        agent_idx = seat_to_agent[seat]

        obs = state.get_observable_state(seat)
        legal = gu.engine.get_legal_moves(state)

        t0 = time.perf_counter()
        action = agents[agent_idx].get_action(obs, legal)
        move_times[agent_idx].append(time.perf_counter() - t0)

        if action not in legal:
            raise ValueError(
                f"Illegal action {action} from {specs[agent_idx]} (seat {seat}). Legal: {legal}"
            )
        if verbose:
            print(f"Seat {seat} ({specs[agent_idx]}) plays {action}")

        state = gu.engine.apply_action(state, action)
        moves += 1

    duration = time.perf_counter() - game_start

    seat_utils = gu.engine.get_utilities(state)
    agent_utils = [0.0] * n
    for seat, agent_idx in enumerate(seat_to_agent):
        agent_utils[agent_idx] = seat_utils[seat]

    if verbose:
        print(f"Utilities by agent: {agent_utils}")

    return {
        "game": game_idx,
        "seed": seed,
        "shift": shift,
        "duration": duration,
        "moves": moves,
        "utilities": agent_utils,
        "move_times": move_times,
    }


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------

def percentile(sorted_vals: Sequence[float], q: float) -> float:
    """Linear-interpolated percentile, q in [0, 1]. Expects sorted input."""
    if not sorted_vals:
        return 0.0
    k = (len(sorted_vals) - 1) * q
    lo, hi = math.floor(k), math.ceil(k)
    if lo == hi:
        return sorted_vals[lo]
    return sorted_vals[lo] + (sorted_vals[hi] - sorted_vals[lo]) * (k - lo)


def summarize(values: Sequence[float]) -> dict[str, float]:
    n = len(values)
    if n == 0:
        return dict(n=0, mean=0.0, std=0.0, sem=0.0, ci95=0.0, min=0.0,
                    p25=0.0, median=0.0, p75=0.0, p95=0.0, max=0.0, total=0.0)
    s = sorted(values)
    std = statistics.stdev(values) if n > 1 else 0.0
    sem = std / math.sqrt(n) if n > 1 else 0.0
    return dict(
        n=n,
        mean=statistics.fmean(values),
        std=std,
        sem=sem,
        ci95=1.96 * sem,
        min=s[0],
        p25=percentile(s, 0.25),
        median=percentile(s, 0.50),
        p75=percentile(s, 0.75),
        p95=percentile(s, 0.95),
        max=s[-1],
        total=sum(values),
    )


def build_summary(results: list[dict], labels: list[str], wall_total: float) -> dict[str, Any]:
    n_agents = len(labels)
    n_games = len(results)

    agents_summary = {}
    for a in range(n_agents):
        utils = [r["utilities"][a] for r in results]
        times = [t for r in results for t in r["move_times"][a]]
        # Per-game total thinking time for this agent
        per_game_think = [sum(r["move_times"][a]) for r in results]

        wins = sum(1 for u in utils if u > 0)
        losses = sum(1 for u in utils if u < 0)
        ties = n_games - wins - losses

        agents_summary[labels[a]] = {
            "utility": summarize(utils),
            "win_rate": wins / n_games if n_games else 0.0,
            "gurka_rate": losses / n_games if n_games else 0.0,
            "tie_rate": ties / n_games if n_games else 0.0,
            "move_time_s": summarize(times),
            "think_time_per_game_s": summarize(per_game_think),
        }

    return {
        "games": n_games,
        "wall_time_total_s": wall_total,
        "game_time_s": summarize([r["duration"] for r in results]),
        "moves_per_game": summarize([float(r["moves"]) for r in results]),
        "agents": agents_summary,
    }


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def print_report(summary: dict[str, Any], config: dict[str, Any]) -> None:
    agents = summary["agents"]
    name_w = max(len("Agent"), *(len(a) for a in agents))

    print()
    print("=" * 78)
    print(f"Games: {summary['games']}   Players: {len(agents)}   "
          f"Hand size: {config['hand_size']}   Seed: {config['seed']}   "
          f"Rotate seats: {config['rotate']}   Workers: {config['workers']}")
    print("=" * 78)

    # Utility table
    print("\nUTILITY PER GAME (higher is better, zero-sum)")
    header = (f"{'Agent':<{name_w}}  {'mean':>8} {'±95%CI':>8} {'std':>8} "
              f"{'min':>8} {'median':>8} {'max':>8}  {'win%':>6} {'gurka%':>7}")
    print(header)
    print("-" * len(header))
    for name, s in agents.items():
        u = s["utility"]
        print(f"{name:<{name_w}}  {u['mean']:>8.3f} {u['ci95']:>8.3f} {u['std']:>8.3f} "
              f"{u['min']:>8.2f} {u['median']:>8.2f} {u['max']:>8.2f}  "
              f"{100 * s['win_rate']:>5.1f}% {100 * s['gurka_rate']:>6.1f}%")

    # Decision time table
    print("\nDECISION TIME PER MOVE (milliseconds)")
    header = (f"{'Agent':<{name_w}}  {'moves':>7} {'mean':>9} {'std':>9} "
              f"{'min':>9} {'median':>9} {'p95':>9} {'max':>9}  {'think/game s':>12}")
    print(header)
    print("-" * len(header))
    for name, s in agents.items():
        t = s["move_time_s"]
        g = s["think_time_per_game_s"]
        print(f"{name:<{name_w}}  {t['n']:>7} {1000 * t['mean']:>9.3f} {1000 * t['std']:>9.3f} "
              f"{1000 * t['min']:>9.3f} {1000 * t['median']:>9.3f} "
              f"{1000 * t['p95']:>9.3f} {1000 * t['max']:>9.3f}  {g['mean']:>12.3f}")

    # Game time
    gt = summary["game_time_s"]
    mv = summary["moves_per_game"]
    print("\nGAME DURATION (seconds)")
    print(f"  mean {gt['mean']:.3f}   std {gt['std']:.3f}   min {gt['min']:.3f}   "
          f"median {gt['median']:.3f}   p95 {gt['p95']:.3f}   max {gt['max']:.3f}")
    print(f"  moves per game: mean {mv['mean']:.1f}   min {mv['min']:.0f}   max {mv['max']:.0f}")
    print(f"  total wall time: {summary['wall_time_total_s']:.2f} s "
          f"({summary['wall_time_total_s'] / max(summary['games'], 1):.3f} s/game effective)")
    print()


def write_csv(path: str, results: list[dict], labels: list[str]) -> None:
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["game", "seed", "shift", "duration_s", "moves"]
                   + [f"utility[{l}]" for l in labels]
                   + [f"think_s[{l}]" for l in labels])
        for r in results:
            w.writerow([r["game"], r["seed"], r["shift"], f"{r['duration']:.6f}", r["moves"]]
                       + r["utilities"]
                       + [f"{sum(t):.6f}" for t in r["move_times"]])


# ---------------------------------------------------------------------------
# Tournament driver
# ---------------------------------------------------------------------------

def run_tournament(
    specs: list[str],
    num_games: int = 50,
    hand_size: int = 7,
    seed: int | None = None,
    rotate: bool = True,
    workers: int = 1,
    verbose: bool = False,
    progress: bool = True,
) -> tuple[list[dict], dict[str, Any], dict[str, Any]]:
    """Run num_games games and return (per-game results, summary, config)."""
    if seed is None:
        seed = random.SystemRandom().randrange(2**31)
    if workers <= 0:
        workers = os.cpu_count() or 1
    workers = min(workers, num_games)

    labels = unique_labels(specs)
    jobs = [(g, seed + g, specs, hand_size, rotate, verbose) for g in range(num_games)]

    results: list[dict] = []
    start = time.perf_counter()

    def report_progress(done: int) -> None:
        if not progress:
            return
        elapsed = time.perf_counter() - start
        eta = elapsed / done * (num_games - done)
        print(f"\rGame {done}/{num_games}  elapsed {elapsed:6.1f}s  eta {eta:6.1f}s",
              end="", file=sys.stderr, flush=True)

    if workers == 1:
        for job in jobs:
            results.append(run_game(job))
            report_progress(len(results))
    else:
        with mp.Pool(workers) as pool:
            for r in pool.imap_unordered(run_game, jobs):
                results.append(r)
                report_progress(len(results))
    if progress:
        print(file=sys.stderr)

    wall_total = time.perf_counter() - start
    results.sort(key=lambda r: r["game"])

    summary = build_summary(results, labels, wall_total)
    config = {"specs": specs, "labels": labels, "num_games": num_games,
              "hand_size": hand_size, "seed": seed, "rotate": rotate, "workers": workers}
    return results, summary, config


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Run a tournament between gursh agents and report statistics.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("-a", "--agents", nargs="+", type=agent_spec,
                   default=["highest", "mixed:maxn=200,mcts=2000,limit=4"],
                   metavar="SPEC",
                   help="agent specs, one per player (default: highest + mixed)")
    p.add_argument("-n", "--num-games", type=int, default=50, help="number of games (default 50)")
    p.add_argument("--hand-size", type=int, default=7, help="cards per player (default 7)")
    p.add_argument("--seed", type=int, default=None,
                   help="base seed; game g uses seed+g, so results are reproducible "
                        "regardless of --workers (default: random, printed in report)")
    p.add_argument("--no-rotate", action="store_true",
                   help="keep agents in fixed seats instead of rotating each game")
    p.add_argument("-j", "--workers", type=int, default=1,
                   help="parallel worker processes; 0 = all CPUs (default 1)")
    p.add_argument("-v", "--verbose", action="store_true",
                   help="print every move (use with -j 1 for readable output)")
    p.add_argument("-q", "--quiet", action="store_true", help="no progress bar")
    p.add_argument("--csv", metavar="PATH", help="write per-game results to a CSV file")
    p.add_argument("--json", metavar="PATH", help="write the summary statistics to a JSON file")

    args = p.parse_args(argv)

    n_players = len(args.agents)
    if n_players < 2:
        p.error("need at least 2 agents")
    if args.num_games < 1:
        p.error("--num-games must be at least 1")
    if args.hand_size < 1:
        p.error("--hand-size must be at least 1")
    if args.hand_size * n_players > 52:
        p.error(f"{n_players} players x {args.hand_size} cards exceeds the 52-card deck")
    return args


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)

    results, summary, config = run_tournament(
        specs=args.agents,
        num_games=args.num_games,
        hand_size=args.hand_size,
        seed=args.seed,
        rotate=not args.no_rotate,
        workers=args.workers,
        verbose=args.verbose,
        progress=not args.quiet,
    )

    print_report(summary, config)

    if args.csv:
        write_csv(args.csv, results, config["labels"])
        print(f"Per-game results written to {args.csv}")
    if args.json:
        with open(args.json, "w") as f:
            json.dump({"config": config, "summary": summary}, f, indent=2)
        print(f"Summary written to {args.json}")


if __name__ == "__main__":
    main()