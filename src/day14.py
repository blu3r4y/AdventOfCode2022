# Advent of Code 2022, Day 14
# (c) blu3r4y

import numpy as np
from aocd.models import Puzzle
from funcy import print_calls, print_durations
from parse import parse

EMPTY, STONE, SAND = 0, 1, 2


@print_calls
@print_durations(unit="ms")
def part1(grid, x=500, y=0):
    return solve(grid, x=x, y=y)


@print_calls
@print_durations(unit="ms")
def part2(grid, pad=500):
    # expand grid 2 in y (to draw a floor) and pad in x to make room for sand
    grid = np.pad(grid, ((0, 2), (pad, pad)), mode="constant", constant_values=EMPTY)
    grid[-1, :] = STONE

    # drop sand until the source is blocked
    return solve(grid, x=500 + pad, y=0)


def solve(grid, x, y):
    count = 0
    while drop(grid, x, y):
        count += 1
    return count


def drop(grid, x, y):
    h, w = grid.shape

    # is the source free?
    if grid[y, x] != EMPTY:
        return False

    while y + 1 < h:
        # can we move down?
        if grid[y + 1, x] == EMPTY:
            y += 1
        # can we move left?
        elif x > 0 and grid[y + 1, x - 1] == EMPTY:
            y += 1
            x -= 1
        # can we move right?
        elif x + 1 < w and grid[y + 1, x + 1] == EMPTY:
            y += 1
            x += 1
        # are we blocked?
        else:
            break

    # will sand flow into the void?
    if y == h - 1:
        return False

    grid[y, x] = SAND
    return True


def load(data):
    traces = []
    for trace in data.split("\n"):
        lines = trace.split(" -> ")
        lines = [parse("{:d},{:d}", line).fixed for line in lines]
        traces.append(lines)

    # build matrix
    w = max([x for x, y in np.concatenate(traces)])
    h = max([y for x, y in np.concatenate(traces)])
    grid = np.full((h + 1, w + 1), fill_value=EMPTY, dtype=int)

    # draw lines
    for trace in traces:
        for (ax, ay), (bx, by) in zip(trace, trace[1:]):
            ay, by = sorted((ay, by))
            ax, bx = sorted((ax, bx))
            grid[ay : by + 1, ax : bx + 1] = STONE

    return grid


if __name__ == "__main__":
    puzzle = Puzzle(year=2022, day=14)

    ans1 = part1(load(puzzle.input_data))
    assert ans1 == 683
    # puzzle.answer_a = ans1

    ans2 = part2(load(puzzle.input_data))
    assert ans2 == 28821
    # puzzle.answer_b = ans2
