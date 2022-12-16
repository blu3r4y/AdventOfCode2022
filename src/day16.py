# Advent of Code 2022, Day 16
# (c) blu3r4y

from collections import namedtuple
from itertools import combinations
from queue import PriorityQueue
from typing import Callable, Dict, Iterable, Optional, Tuple

import networkx as nx
from aocd.models import Puzzle
from funcy import print_calls
from parse import parse
from tqdm import tqdm

Valve = namedtuple("Valve", ["name", "flow", "childs"])
State = namedtuple("State", ["curr", "pre", "min", "press", "closed"])

ACTOR1, ACTOR2 = 0, 1


class Solver:
    def __init__(self, valves: Dict[str, Valve]):
        self.valves = valves
        self.childs = None
        self.flows = None
        self.dist = None

    def _prepare_fields(self, start: str, transitive: bool = False):
        G, dist = Solver._build_graph(self.valves, start, transitive)

        # only the extract graph properties which we actually need
        self.nodes = list(G.nodes)
        self.childs = {n: list(nx.neighbors(G, n)) for n in G.nodes}
        self.flows = {n: self.valves[n].flow for n in G.nodes}
        self.dist = dist

    def solve(self, start: str, total_minutes: int, two_actors: bool = False) -> int:
        self._prepare_fields(start, transitive=not two_actors)

        # map start string to state
        curr = start if not two_actors else (start, start)
        pre = None if not two_actors else (None, None)
        state = State(curr, pre, total_minutes, 0, frozenset(self.nodes))

        succ_func = self.successors_two if two_actors else self.successors_one
        est_func = self.estimate_press_two if two_actors else self.estimate_press_one
        goal = Solver.astar_search(state, succ_func, est_func, progress=two_actors)
        return goal.press

    ###########################################################################

    @staticmethod
    def astar_search(
        start: State,
        successors_func: Callable[[State], Iterable[State]],
        estimator_func: Callable[[State], int],
        progress: bool = False,
    ) -> State:
        # perform an A* search on the inverse graph, i.e.,
        # maximize the pressure be minimizing the negative pressure
        openpq = PriorityQueue()
        openpq.put((0, start))
        closed = {start: 0}

        negative_pressure, goal = None, None

        with tqdm(unit="states", disable=not progress) as pbar:
            while not openpq.empty():
                negative_pressure, current = openpq.get()
                if Solver.is_goal(current):
                    goal = current
                    break

                # just update the progress bar
                pbar.set_postfix(total_pressure=-negative_pressure, refresh=False)
                pbar.update()

                for succ in successors_func(current):
                    if succ not in closed or succ.press > closed[succ]:
                        closed[succ] = succ.press
                        estimate = succ.press + estimator_func(succ)
                        openpq.put((-estimate, succ))

        assert goal.press == -negative_pressure
        return goal

    @staticmethod
    def is_goal(s: State) -> bool:
        return s.min == 0 or len(s.closed) == 0

    ###########################################################################

    def estimate_press_one(self, s: State) -> int:
        estimate = 0
        for target in s.closed:
            dist = self.dist[s.curr][target]
            estimate += max(0, s.min - dist) * self.flows[target]

        # make sure that we overestimate the pressure
        return estimate

    def estimate_press_two(self, s: State):
        estimate = 0
        for target in s.closed:
            dist = min(
                self.dist[s.curr[ACTOR1]][target],
                self.dist[s.curr[ACTOR2]][target],
            )
            estimate += max(0, s.min - dist) * self.flows[target]

        # make sure that we overestimate the pressure
        return estimate

    ###########################################################################

    def successors_one(self, s: State) -> Iterable[State]:
        if s.min == 0:
            return

        # if this valve has positive flow, can we still open it?
        if (released := self.released_pressure(s, s.curr)) is not None:
            nxt_press = s.press + released
            nxt_closed = s.closed - {s.curr}
            yield State(s.curr, s.curr, s.min - 1, nxt_press, nxt_closed)

        # what neighbouring valves can we visit?
        for nxt in self.childs[s.curr]:
            steps = self.dist[s.curr][nxt]
            yield State(nxt, s.curr, max(0, s.min - steps), s.press, s.closed)

    def successors_two(self, s: State) -> Iterable[State]:
        if s.min == 0:
            return

        # each actor tries opening the valves
        released1 = self.released_pressure(s, s.curr[ACTOR1])
        released2 = self.released_pressure(s, s.curr[ACTOR2])

        remaining_min = s.min - 1

        # state when both actors open a valve (but not the same one)
        if (
            s.curr[ACTOR1] != s.curr[ACTOR2]
            and released1 is not None
            and released2 is not None
        ):
            nxt_press = s.press + released1 + released2
            nxt_closed = s.closed - set(s.curr)
            yield State(s.curr, s.curr, remaining_min, nxt_press, nxt_closed)

        for n1 in self.childs[s.curr[ACTOR1]]:
            for n2 in self.childs[s.curr[ACTOR2]]:

                # state when actor 1 moves, but actor 2 opens a valve
                if released2 is not None:
                    if n1 == s.pre[ACTOR1]:
                        continue  # don't move back

                    nxt = (n1, s.curr[ACTOR2])
                    nxt_press = s.press + released2
                    nxt_closed = s.closed - {s.curr[ACTOR2]}
                    yield State(nxt, s.curr, remaining_min, nxt_press, nxt_closed)

                # state when actor 2 moves, but actor 1 opens a valve
                if released1 is not None:
                    if n2 == s.pre[ACTOR2]:
                        continue  # don't move back

                    nxt = (s.curr[ACTOR1], n2)
                    nxt_press = s.press + released1
                    nxt_closed = s.closed - {s.curr[ACTOR1]}
                    yield State(nxt, s.curr, remaining_min, nxt_press, nxt_closed)

        # states when both actors move
        for n1 in self.childs[s.curr[ACTOR1]]:
            for n2 in self.childs[s.curr[ACTOR2]]:
                if n1 == s.pre[ACTOR1] or n2 == s.pre[ACTOR2]:
                    continue  # don't move back

                yield State((n1, n2), s.curr, remaining_min, s.press, s.closed)

    def released_pressure(self, s: State, node) -> Optional[int]:
        flow = self.flows[node]
        if flow > 0 and node in s.closed:
            return flow * (s.min - 1)

    ###########################################################################

    @staticmethod
    def _build_graph(
        valves: Dict[str, Valve], start: str, transitive: bool
    ) -> Tuple[nx.Graph, Dict[str, Dict[str, int]]]:
        G = nx.Graph()
        for valve in valves.values():
            for child in valve.childs:
                G.add_edge(valve.name, child, weight=1)

        # compute all shortest paths and possible reduce to transitive closure
        dist = dict(nx.all_pairs_shortest_path_length(G))
        if transitive:
            for node in valves.keys():
                if valves[node].flow == 0 and node != start:
                    # remove valve and reconnect neighbours
                    for a, b in combinations(G.neighbors(node), 2):
                        G.add_edge(a, b, weight=dist[a][b])
                    G.remove_node(node)

        return G, dist


@print_calls
def part1(valves, total_minutes=30):
    return Solver(valves).solve("AA", total_minutes)


@print_calls
def part2(valves, total_minutes=26):
    return Solver(valves).solve("AA", total_minutes, two_actors=True)


def load(data):
    pattern1 = "Valve {} has flow rate={:d}; tunnels lead to valves {}"
    pattern2 = "Valve {} has flow rate={:d}; tunnel leads to valve {}"

    valves = {}
    for line in data.splitlines():
        name, flow, childs = None, None, None

        # parse plural string
        if p1 := parse(pattern1, line):
            name, flow, childs = p1.fixed
            childs = childs.split(", ")

        # parse singular string
        elif p2 := parse(pattern2, line):
            name, flow, child = p2.fixed
            childs = [child]

        assert name is not None
        assert flow is not None
        assert childs is not None
        valves[name] = Valve(name, flow, childs)

    return valves


if __name__ == "__main__":
    puzzle = Puzzle(year=2022, day=16)

    ans1 = part1(load(puzzle.input_data))
    assert ans1 == 1873
    # puzzle.answer_a = ans1

    ans2 = part2(load(puzzle.input_data))
    assert ans2 == 2425
    # puzzle.answer_b = ans2
