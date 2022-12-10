# Advent of Code 2022, Day 10
# (c) blu3r4y

import matplotlib.pyplot as plt
import numpy as np
from aocd.models import Puzzle
from funcy import collecting, print_calls
from parse import parse


@print_calls
def part1(instructions):
    cycles = simulate(instructions)

    strength = 0
    for i in range(1, len(cycles)):
        if (i + 20) % 40 == 0:
            strength += i * cycles[i]

    return strength


@print_calls
def part2(instructions):
    # use zero-based indexing again
    cycles = simulate(instructions)[1:]

    i = 0
    crt = np.zeros((6, 40), dtype=int)
    for row in range(6):
        for col in range(40):
            # is the sprite hovering over the crt pixel?
            if cycles[i] - 1 <= col <= cycles[i] + 1:
                crt[row][col] = 1
            i += 1

    plt.imshow(crt, cmap="gray")
    plt.show()


def simulate(instructions):
    # to make indexing easier, we
    # add a placeholder at index 0
    xs, x = [None], 1

    for ins in instructions:
        xs.append(x)
        if ins != 0:
            xs.append(x)
            x += ins

    return xs


@collecting
def load(data):
    for line in data.split("\n"):
        if line.startswith("addx"):
            yield parse("addx {:d}", line)[0]
        elif line.startswith("noop"):
            yield 0


if __name__ == "__main__":
    puzzle = Puzzle(year=2022, day=10)

    ans1 = part1(load(puzzle.input_data))
    assert ans1 == 14920
    # puzzle.answer_a = ans1
    ans2 = part2(load(puzzle.input_data))
    # assert ans2 == "BUCACBUZ"
    # puzzle.answer_b = ans2
