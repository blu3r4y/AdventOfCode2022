# Advent of Code 2022, Day 6
# (c) blu3r4y

from aocd.models import Puzzle
from funcy import partition, print_calls


def solve(data, size):
    # report the index after the
    # first block of only unique characters
    for part in partition(size, 1, data):
        if len(set(part)) == len(part):
            return data.index(part) + size


@print_calls
def part1(data):
    return solve(data, 4)


@print_calls
def part2(data):
    return solve(data, 14)


def load(data):
    return data


if __name__ == "__main__":
    puzzle = Puzzle(year=2022, day=6)

    ans1 = part1(load(puzzle.input_data))
    assert ans1 == 1080
    # puzzle.answer_a = ans1
    ans2 = part2(load(puzzle.input_data))
    assert ans2 == 3645
    # puzzle.answer_b = ans2
