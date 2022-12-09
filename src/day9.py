# Advent of Code 2022, Day 9
# (c) blu3r4y

from collections import namedtuple

import numpy as np
from aocd.models import Puzzle
from funcy import collecting, print_calls
from parse import parse

Move = namedtuple("Move", ["dir", "len"])


@print_calls
def part1(moves):
    return solve(moves, nknots=2)


@print_calls
def part2(moves):
    return solve(moves, nknots=10)


def solve(moves, nknots):
    knots = [0j] * nknots
    visited = set()

    for move in moves:

        # make one step at a time
        step = Move(move.dir, 1)
        for _ in range(move.len):

            # advance head of the rope
            knots[0] = advance(knots[0], step)

            # trace along the other knots, if they are not adjacent
            for k in range(1, len(knots)):
                if not adjacent(knots[k], knots[k - 1]):
                    knots[k] = trace(knots[k], knots[k - 1])

            # note positions of the last knot (the tail)
            visited.add(knots[-1])

    return len(visited)


def adjacent(a, b):
    return abs(a - b) < 2


def trace(a: complex, b: complex):
    vec = b - a
    return a + np.sign(vec.real) + 1j * np.sign(vec.imag)


def advance(pos, move):
    if move.dir == "R":
        return pos + move.len
    elif move.dir == "L":
        return pos - move.len
    elif move.dir == "U":
        return pos + 1j * move.len
    elif move.dir == "D":
        return pos - 1j * move.len
    else:
        raise ValueError(f"invalid direction: {move.dir}")


@collecting
def load(data):
    for line in data.split("\n"):
        yield Move(*parse("{} {:d}", line).fixed)


if __name__ == "__main__":
    puzzle = Puzzle(year=2022, day=9)

    ans1 = part1(load(puzzle.input_data))
    assert ans1 == 6081
    # puzzle.answer_a = ans1
    ans2 = part2(load(puzzle.input_data))
    assert ans2 == 2487
    # puzzle.answer_b = ans2
