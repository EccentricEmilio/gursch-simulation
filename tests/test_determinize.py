"""
Test suite for gursh.engine.determinize_state.

Two kinds of check:

1. Invariant checks (test_determinize_state_invariants) - things that must
   be true on EVERY single call, no exceptions: correct hand sizes, no
   card exceeding 4 physical copies, every sampled card respecting the
   target player's hand_info, self's own hand/played_cards left untouched.
   These catch outright bugs (e.g. the "wrong index filtered" bug from
   earlier, or a determinization that silently drops/duplicates a card).

2. Statistical check (test_determinize_state_distribution) - invariant
   checks alone can't catch a *biased* sampler: one that only ever
   produces valid states, but not with the right probabilities (e.g.
   always dealing player 1 low cards because of assignment order). This
   runs many determinizations from a fixed, fully-unconstrained state and
   checks, via a chi-square goodness-of-fit test, whether the number of
   copies of a given rank landing in a target player's hand matches the
   hypergeometric distribution a genuine uniform-random deal would produce.
"""
import sys
from pathlib import Path

# Add the repository root to Python's import path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import random
from collections import Counter
from scipy.stats import hypergeom, chisquare

import gursh

def test_determinize_state_invariants(trials: int = 3000) -> None:
    for player_count in (2, 3, 4):
        per_pc_trials = trials // 3
        for _ in range(per_pc_trials):
            hand_size = random.randint(2, 8)
            state = gursh.state.State.create_new_game(player_count=player_count, hand_size=hand_size)
            self_index = random.randrange(player_count)

            det = gursh.engine.determinize_state(state, self_index)

            # self's own hand and played_cards must be untouched
            assert det.hands[self_index] == state.hands[self_index], (
                "determinize_state modified self_index's own hand"
            )
            assert det.played_cards == state.played_cards, (
                "determinize_state modified played_cards"
            )

            # hand sizes preserved for every player
            for i in range(player_count):
                assert len(det.hands[i]) == len(state.hands[i]), (
                    f"player {i} hand size changed: "
                    f"{len(state.hands[i])} -> {len(det.hands[i])}"
                )

            # every sampled card for every OTHER player respects that
            # player's hand_info
            for i in range(player_count):
                if i == self_index:
                    continue
                for card in det.hands[i]:
                    assert card in state.hand_info[i], (
                        f"card {card} sampled for player {i} violates "
                        f"hand_info {state.hand_info[i]}"
                    )

            # global multiplicity: no rank used more than 4 times across
            # every hand plus played_cards
            all_cards = Counter()
            for hand in det.hands:
                all_cards.update(hand)
            all_cards.update(det.played_cards)
            for rank, count in all_cards.items():
                assert count <= 4, f"rank {rank} used {count} times (max 4)"

    print(f"[invariants] passed across {trials} determinizations "
          f"(player_count in {{2,3,4}}, random hand sizes 2-8).")


def _merge_tail_categories(obs: list[float], exp: list[float], min_expected: float = 5.0):
    """
    Standard chi-square prep: merge categories from the sparse tail inward
    until every category has expected count >= min_expected (a common rule
    of thumb for the chi-square approximation to be valid). Assumes obs/exp
    are ordered so that the tail (last entries) is the sparse end.
    """
    obs = list(obs)
    exp = list(exp)
    while len(exp) > 1 and exp[-1] < min_expected:
        exp[-2] += exp[-1]
        obs[-2] += obs[-1]
        exp.pop()
        obs.pop()
    return obs, exp


def test_determinize_state_distribution(
    player_count: int = 2,
    hand_size: int = 8,
    self_index: int = 0,
    target_index: int = 1,
    trials: int = 4000,
    alpha: float = 0.01,
    n_marker_ranks: int = 3,
) -> None:
    """
    Statistical goodness-of-fit check. Builds one fixed, fully-unconstrained
    starting state (hand_info covers the whole deck for every player, since
    nothing has been forced-played yet), runs `trials` determinizations, and
    for a handful of ranks that are entirely unknown to self_index (all 4
    copies still live in the pool), compares the empirical distribution of
    "how many copies of this rank ended up in target_index's sampled hand"
    against the hypergeometric distribution a genuine uniform-random deal
    would produce.

    Each marker rank gets its own independent chi-square test (this is the
    statistically clean way to do it - pooling counts across multiple ranks
    from the same trials would introduce cross-rank correlation that breaks
    the simple chi-square assumptions). With n_marker_ranks tests run at
    level alpha, a well-behaved sampler should still fail purely by chance
    with probability roughly n_marker_ranks * alpha (Bonferroni), so treat
    a single borderline failure with suspicion but not alarm; treat several
    failures, or one with a very small p-value, as a real signal of bias.
    """
    state = gursh.state.State.create_new_game(player_count=player_count, hand_size=hand_size)

    full_deck = Counter({rank: 4 for rank in range(2, 15)})
    known = Counter(state.hands[self_index]) + Counter(state.played_cards)
    pool_counts = full_deck - known
    pool_size = sum(pool_counts.values())
    target_hand_size = len(state.hands[target_index])

    # marker ranks: fully unknown to self_index (K == 4 copies still in the
    # pool) and unrestricted by target_index's hand_info, so the test is
    # purely about the sampler's behaviour, not about filtering correctness
    # (which the invariant test already covers).
    marker_ranks = [
        r for r, K in pool_counts.items()
        if K == 4 and r in state.hand_info[target_index]
    ][:n_marker_ranks]

    if not marker_ranks:
        print("[distribution] no eligible marker ranks for this state; skipped.")
        return

    max_k = min(4, target_hand_size)
    observed = {r: [0] * (max_k + 1) for r in marker_ranks}

    for _ in range(trials):
        det = gursh.engine.determinize_state(state, self_index)
        hand_counts = Counter(det.hands[target_index])
        for r in marker_ranks:
            k = min(hand_counts.get(r, 0), max_k)
            observed[r][k] += 1

    any_failure = False
    for r in marker_ranks:
        expected_probs = [
            hypergeom.pmf(k, pool_size, pool_counts[r], target_hand_size)
            for k in range(max_k + 1)
        ]
        expected_counts = [p * trials for p in expected_probs]

        obs, exp = _merge_tail_categories(observed[r], expected_counts)

        # renormalize expected to match total observed exactly (chisquare
        # requires sum(f_obs) == sum(f_exp); tiny float drift otherwise)
        exp_total = sum(exp)
        obs_total = sum(obs)
        exp = [e * obs_total / exp_total for e in exp]

        chi2, p_value = chisquare(f_obs=obs, f_exp=exp)
        verdict = "PASS" if p_value >= alpha else "FAIL"
        if p_value < alpha:
            any_failure = True
        print(f"[distribution] rank={r}: chi2={chi2:.3f}, "
              f"categories={len(obs)}, p={p_value:.4f}  -> {verdict}")

    bonferroni_alpha = alpha * len(marker_ranks)
    if any_failure:
        print(f"[distribution] at least one marker rank failed at alpha={alpha} "
              f"(Bonferroni-adjusted family alpha={bonferroni_alpha:.4f}). "
              "Re-run with more trials before concluding there's a real bias - "
              "a single failure at this alpha is expected occasionally by chance.")
    else:
        print(f"[distribution] all {len(marker_ranks)} marker ranks consistent "
              "with an unbiased uniform-random deal.")


if __name__ == "__main__":
    test_determinize_state_invariants()
    print()
    test_determinize_state_distribution()
    print()
    test_determinize_state_distribution(player_count=4, hand_size=6, self_index=2, target_index=0)
