import math
import random
from . import engine
from .state import State


class Node:
    __slots__ = ("children", "visits", "availability", "totals")

    def __init__(self, n_players: int):
        self.children: dict[tuple[int, ...], "Node"] = {}
        self.visits = 0
        self.availability = 0            # times this move was legal when its parent was visited
        self.totals = [0.0] * n_players  # summed (normalized) utilities per player


def _ucb(child: Node, player: int, c: float) -> float:
    # Exploitation: average result for the player who is choosing this move
    exploit = child.totals[player] / child.visits
    # Exploration: bonus for moves that have been tried rarely. Uses availability
    # instead of the parent's visits, since a move is only legal in some determinizations.
    explore = c * math.sqrt(math.log(child.availability) / child.visits)
    return exploit + explore


def get_rollout_move(legal_moves: list[tuple[int, ...]]) -> tuple[int, ...]:
    # Rollout policy: pick a random legal move. This is the default for SO-ISMCTS.
    # This could be replaced with a more sophisticated rollout policy, e.g. one that prefers higher cards or longer runs, but that would bias the search and might not be optimal for all players.
    # Could be improved by using a heuristic to choose a move, e.g. highest card, longest run, etc.
    return random.choice(legal_moves)




def choose_move_mcts(state: State, iterations: int = 1000, c: float = 0.7) -> dict[tuple[int, ...], int]:
    '''
    SO-ISMCTS from the perspective of state.current_player.
    Returns {root_action: visit_count}; pick the max for the "robust child".
    '''
    root_player = state.current_player
    n = len(state.hands)
    root = Node(n)
    # Utilities are bounded by roughly (highest card) * (cards in the last trick),
    # so scale to ~[-1, 1] so that c=0.7 is meaningful.
    scale = 14.0 * max(len(h) for h in state.hands)

    for _ in range(iterations):
        # --- Determinization: sample one possible world consistent with what
        # root_player knows. Everything below happens inside this one world. ---
        det = engine.determinize_state(state, root_player)
        node = root
        path: list[Node] = []   # nodes visited this iteration, for backpropagation
        expanded = False        # True once we have left the tree (expansion done)

        while not det.is_game_over():
            legal = engine.get_legal_moves(det)

            if not expanded:
                # Phase 1 (SELECTION) and Phase 2 (EXPANSION): we are still
                # inside the tree, so pick moves with the tree policy.
                player = det.current_player

                # Count that each existing child was available this time
                for a in legal:
                    if a in node.children:
                        node.children[a].availability += 1

                untried = [a for a in legal if a not in node.children]
                if untried:
                    # Phase 2: EXPANSION. Some legal move has no node yet, so
                    # add one new child for it. Only one node is added per
                    # iteration, after which we leave the tree.
                    action = random.choice(untried)
                    child = Node(n)
                    child.availability = 1
                    node.children[action] = child
                    expanded = True
                else:
                    # Phase 1: SELECTION. Every legal move already has a node,
                    # so choose among them by UCB for the player to move, then
                    # keep descending.
                    action = max(legal, key=lambda a: _ucb(node.children[a], player, c))

                node = node.children[action]
                path.append(node)
            else:
                # Phase 3: SIMULATION (rollout). We are outside the tree, so
                # play random moves until the game ends. Nothing is stored here.

                action = get_rollout_move(legal)

            det = engine.apply_action(det, action)

        # Phase 4: BACKPROPAGATION. Take the final utilities of the finished
        # game and add them to every node on the path we walked. Each node
        # stores the full vector, so each player's own component is available
        # later when that player is choosing a move.
        utils = engine.get_utilities(det)
        for nd in path:
            nd.visits += 1
            for i in range(n):
                nd.totals[i] += utils[i] / scale

    return {a: ch.visits for a, ch in root.children.items()}