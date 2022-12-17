# Advent of Code 2022, Day 16
# (c) blu3r4y

from collections import namedtuple
from functools import cache
from itertools import combinations
from typing import Dict, Tuple

import networkx as nx
from aocd.models import Puzzle
from funcy import print_calls, print_durations
from parse import parse

Valve = namedtuple("Valve", ["name", "flow", "childs"])
State = namedtuple("State", ["position", "minute", "pressure", "available"])

DistDict = Dict[str, Dict[str, int]]


class Solver:
    def __init__(self, valves: Dict[str, Valve], start: str):
        # prepare distance and flow dictionaries for fast lookup
        G, dist = Solver._build_graph(valves, start)
        self.flows = {n: valves[n].flow for n in G.nodes}
        self.nodes = frozenset(G.nodes) - {start}
        self.start = start
        self.dist = dist

    def solve_human(self, total_minutes: int) -> int:
        start = State(self.start, total_minutes, 0, self.nodes)
        return self.ddfs(start, with_elephant=False)

    def solve_human_and_elephant(self, total_minutes: int) -> int:
        start = State(self.start, total_minutes, 0, self.nodes)
        return self.ddfs(start, with_elephant=True)

    @cache
    def ddfs(self, node: State, with_elephant):
        # doing a depth-first search is the best approximation that we have here
        # https://en.wikipedia.org/wiki/Longest_path_problem#Parameterized_complexity
        maximum = 0
        for s in self.successors(node):
            inner = s.pressure + self.ddfs(s, with_elephant)
            maximum = max(maximum, inner)

        # how much could the elephant do in the same time
        # given the valves that the human already opened
        elephant = State(self.start, 26, 0, node.available)
        emax = self.ddfs(elephant, with_elephant=False) if with_elephant else 0

        return max(maximum, emax)

    def successors(self, node: State):
        for target in node.available:
            # time it takes to get to the target and open the valve
            # and total pressure that is released additionally
            duration = self.dist[node.position][target] + 1
            if duration <= node.minute:
                pressure = (node.minute - duration) * self.flows[target]
                yield State(
                    position=target,
                    minute=node.minute - duration,
                    pressure=pressure,
                    available=node.available - {target},
                )

    @staticmethod
    def _build_graph(valves: Dict[str, Valve], start: str) -> Tuple[nx.Graph, DistDict]:
        G = nx.Graph()
        for valve in valves.values():
            for child in valve.childs:
                G.add_edge(valve.name, child, weight=1)

        # compute all shortest paths and reduce to transitive
        # closure, i.e. skip valves that have zero flow entirely
        dist = dict(nx.all_pairs_shortest_path_length(G))
        for node in valves.keys():
            if valves[node].flow == 0 and node != start:
                for a, b in combinations(G.neighbors(node), 2):
                    G.add_edge(a, b, weight=dist[a][b])
                G.remove_node(node)

        return G, dist


@print_calls
@print_durations(unit="ms")
def part1(valves):
    return Solver(valves, "AA").solve_human(30)


@print_calls
@print_durations(unit="ms")
def part2(valves):
    return Solver(valves, "AA").solve_human_and_elephant(26)


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
