# Advent of Code 2022, Day 23
# (c) blu3r4y

from collections import defaultdict
from typing import Set

from aocd.models import Puzzle
from funcy import count, print_calls, print_durations

N, NE, E, SE, S, SW, W, NW = -1j, 1 - 1j, 1, 1 + 1j, 1j, 1j - 1, -1, -1 - 1j
DIRECTIONS = [N, NE, E, SE, S, SW, W, NW]


@print_calls
@print_durations(unit="ms")
def part1(elves: Set[complex]):
    # simulate a maximum of 10 rounds
    simulate(elves, round_limit=10)

    # bounding box around elves
    xs, ys = [int(e.real) for e in elves], [int(e.imag) for e in elves]
    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)

    # count free cells
    nfree = (xmax - xmin + 1) * (ymax - ymin + 1) - len(elves)
    return nfree


@print_calls
@print_durations(unit="ms")
def part2(elves: Set[complex]):
    # round number until no more elves can move
    return simulate(elves, round_limit=float("inf"))


def simulate(elves: Set[complex], round_limit: int | float):
    # consideration and proposal order
    propose, index = [N, S, W, E], 0
    consider = [
        lambda e: e + N not in elves and e + NE not in elves and e + NW not in elves,
        lambda e: e + S not in elves and e + SE not in elves and e + SW not in elves,
        lambda e: e + W not in elves and e + NW not in elves and e + SW not in elves,
        lambda e: e + E not in elves and e + NE not in elves and e + SE not in elves,
    ]

    for rnd in count():
        if rnd >= round_limit:
            return rnd + 1

        moves, noverlaps = [], defaultdict(int)
        for elf in elves:

            # skip if no elves are around
            neighbors = (elf + d for d in DIRECTIONS)
            if all(n not in elves for n in neighbors):
                continue

            # make move proposal
            move = None
            for rnd in range(index, index + 4):
                rnd = rnd % 4
                if consider[rnd](elf):
                    move = propose[rnd]
                    break

            if move is not None:
                moves.append((elf, move))
                noverlaps[elf + move] += 1

        # no more elves to move or round limit reached
        if len(moves) == 0:
            return rnd + 1

        # perform moves
        for elf, move in moves:
            if noverlaps[elf + move] > 1:
                continue
            elves.remove(elf)
            elves.add(elf + move)

        # rotate consideration order
        index = (index + 1) % 4


def load(data) -> Set[complex]:
    elves = set()
    for y, row in enumerate(data.split("\n")):
        for x, cell in enumerate(row):
            if cell == "#":
                elves.add(x + y * 1j)
    return elves


if __name__ == "__main__":
    puzzle = Puzzle(year=2022, day=23)

    ans1 = part1(load(puzzle.input_data))
    assert ans1 == 4049
    # puzzle.answer_a = ans1

    ans2 = part2(load(puzzle.input_data))
    assert ans2 == 1021
    # puzzle.answer_b = ans2
