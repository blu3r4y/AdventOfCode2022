# Advent of Code 2022, Day 8
# (c) blu3r4y

from collections import defaultdict
from typing import Literal, Tuple, get_args

import numpy as np
from aocd.models import Puzzle
from funcy import ilen, print_calls

Orientation = Literal["top", "left", "bot", "right"]


@print_calls
def part1(grid):
    visible = set()
    los = line_of_sight_skyline

    # we stand on the left and right edge, looking 'inward'
    for row in range(grid.shape[0]):
        visible.update(visible_trees_from(grid, (row, 0), "left", los))
        visible.update(visible_trees_from(grid, (row, grid.shape[1] - 1), "right", los))

    # we stand on the top and bot edge, looking 'inward'
    for col in range(grid.shape[1]):
        visible.update(visible_trees_from(grid, (0, col), "top", los))
        visible.update(visible_trees_from(grid, (grid.shape[0] - 1, col), "bot", los))

    return len(visible)


@print_calls
def part2(grid):
    scores = defaultdict(lambda: 1)
    los = line_of_sight_treehouse

    # we stand at every possible position and look 'outwards'
    for row in range(grid.shape[0]):
        for col in range(grid.shape[1]):
            for orient in get_args(Orientation):
                visible_trees = visible_trees_from(grid, (row, col), orient, los)
                viewing_distance = ilen(visible_trees)
                scores[(row, col)] *= viewing_distance

    # best scenic score
    return max(scores.values())


def visible_trees_from(grid, start: Tuple[int, int], orient: Orientation, los_func):
    x, y = start

    if orient == "top":
        visible = los_func(grid[x:, y])
        return ((vis, y) for vis in visible)
    elif orient == "left":
        visible = los_func(grid[x, y:])
        return ((x, vis) for vis in visible)
    elif orient == "bot":
        visible = los_func(grid[x::-1, y])
        return ((grid.shape[1] - 1 - vis, y) for vis in visible)
    elif orient == "right":
        visible = los_func(grid[x, y::-1])
        return ((x, grid.shape[0] - 1 - vis) for vis in visible)


def line_of_sight_skyline(arr):
    """
    Line of sight with the "skyline" method from part 1, i.e., we can see
    everything that is not occluding our POV until we can't see any more.
    The first item in the array will always be seen.
    """
    highest, visible = -1, []

    for i, t in enumerate(arr):
        if t > highest:
            visible.append(i)
        highest = max(t, highest)

    return visible


def line_of_sight_treehouse(arr):
    """
    Line of sight with the "treehouse" method from part 2, i.e., we can see
    below our POV and we stop at the first tree that is the same height or
    taller than our point of view. The first item is the POV and is not seen.
    """
    pov = arr[0]
    highest, visible = 0, []

    for i, t in enumerate(arr[1:]):
        # we can see trees at least as high as our pov
        # or trees higher than the highest tree we have seen
        if t <= pov or t > highest:
            visible.append(i)
        # stop at the first tree equal or above our pov
        if t >= pov:
            break

        highest = max(t, highest)

    return visible


def load(data):
    return np.array([list(map(int, line)) for line in data.split("\n")])


if __name__ == "__main__":
    puzzle = Puzzle(year=2022, day=8)

    ans1 = part1(load(puzzle.input_data))
    assert ans1 == 1763
    # puzzle.answer_a = ans1
    ans2 = part2(load(puzzle.input_data))
    assert ans2 == 671160
    # puzzle.answer_b = ans2
