# Advent of Code 2022, Day 4
# (c) blu3r4y

from aocd.models import Puzzle
from funcy import collecting, print_calls
from parse import parse


@print_calls
def part1(pairs):
    count = 0
    for a1, a2, b1, b2 in pairs:
        # does one range fully contain the other?
        if (a1 <= b1 <= a2 and a1 <= b2 <= a2) or (b1 <= a1 <= b2 and b1 <= a2 <= b2):
            count += 1

    return count


@print_calls
def part2(pairs):
    count = 0
    for a1, a2, b1, b2 in pairs:
        # do ranges overlap?
        if b1 <= a2 and a1 <= b2:
            count += 1

    return count


@collecting
def load(data):
    for line in data.split("\n"):
        yield parse("{:d}-{:d},{:d}-{:d}", line).fixed


if __name__ == "__main__":
    puzzle = Puzzle(year=2022, day=4)

    ans1 = part1(load(puzzle.input_data))
    assert ans1 == 413
    # puzzle.answer_a = ans1
    ans2 = part2(load(puzzle.input_data))
    assert ans2 == 806
    # puzzle.answer_b = ans2
