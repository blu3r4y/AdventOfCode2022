# Advent of Code 2022, Day 12
# (c) blu3r4y

from collections import defaultdict

import networkx as nx
from aocd.models import Puzzle
from funcy import print_calls, print_durations


@print_calls
@print_durations(unit="ms")
def part1(graph, pos):
    start, end = pos["S"][0], pos["E"][0]
    return nx.shortest_path_length(graph, start, end)


@print_calls
@print_durations(unit="ms")
def part2(graph, pos):
    # fewest steps from any "a" node to "z" node
    end, lengths = pos["E"][0], []
    for xy in pos["a"]:
        try:
            length = nx.shortest_path_length(graph, xy, end)
            lengths.append(length)
        except nx.NetworkXNoPath:
            pass

    return min(lengths)


def load(data):
    graph, pos = nx.DiGraph(), defaultdict(list)

    # map letters to (x, y) coordinates with height
    for y, line in enumerate(data.splitlines()):
        for x, c in enumerate(line):
            pos[c].append((x, y))
            c = c.replace("S", "a").replace("E", "z")
            graph.add_node((x, y), height=ord(c))

    # add edge if destination is reachable
    for x, y in graph.nodes:
        src = x, y
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            dst = x + dx, y + dy
            if dst in graph:
                hsrc = graph.nodes[src]["height"]
                hdst = graph.nodes[dst]["height"]

                # add edge if destination is at most one higher
                if hsrc + 1 >= hdst:
                    graph.add_edge(src, dst)

    return graph, pos


if __name__ == "__main__":
    puzzle = Puzzle(year=2022, day=12)

    ans1 = part1(*load(puzzle.input_data))
    assert ans1 == 425
    # puzzle.answer_a = ans1

    ans2 = part2(*load(puzzle.input_data))
    assert ans2 == 418
    # puzzle.answer_b = ans2
