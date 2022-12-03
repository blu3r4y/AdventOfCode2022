# Advent of Code 2022, Day 3
# (c) blu3r4y

from aocd.models import Puzzle
from funcy import first, partition, print_calls


@print_calls
def part1(rucksacks):
    total = 0
    for sack in rucksacks:
        # split rucksack in half and find common item
        a, b = sack[: len(sack) // 2], sack[len(sack) // 2 :]
        a, b = set(a), set(b)
        common_item = first(a & b)
        total += priority(common_item)

    return total


@print_calls
def part2(rucksacks):
    total = 0
    for a, b, c in partition(3, rucksacks):
        # iterate in groups of 3 and find common item
        a, b, c = set(a), set(b), set(c)
        common_item = first(a & b & c)
        total += priority(common_item)

    return total


LOWER_OFFSET = ord("a") - 1
UPPER_OFFSET = ord("A") - 27


def priority(chr):
    # maps a-z to 1-26 and A-Z to 27-52
    return ord(chr) - LOWER_OFFSET if chr.islower() else ord(chr) - UPPER_OFFSET


def load(data):
    return data.split("\n")


if __name__ == "__main__":
    puzzle = Puzzle(year=2022, day=3)

    ans1 = part1(load(puzzle.input_data))
    assert ans1 == 8109
    # puzzle.answer_a = ans1
    ans2 = part2(load(puzzle.input_data))
    assert ans2 == 2738
    # puzzle.answer_b = ans2
