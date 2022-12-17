# Advent of Code 2022, Day 1
# (c) blu3r4y

from aocd.models import Puzzle
from funcy import print_calls, print_durations


@print_calls
@print_durations(unit="ms")
def part1(elves):
    calories = []
    for elf in elves:
        amount = sum(map(int, elf.split()))
        calories.append(amount)

    # how many calories is the top elf carrying?
    return max(calories)


@print_calls
@print_durations(unit="ms")
def part2(elves):
    calories = []
    for elf in elves:
        amount = sum(map(int, elf.split()))
        calories.append(amount)

    # how many calories are the top three elves carrying?
    return sum(sorted(calories, reverse=True)[:3])


def load(data):
    return data.split("\n\n")


if __name__ == "__main__":
    puzzle = Puzzle(year=2022, day=1)

    ans1 = part1(load(puzzle.input_data))
    assert ans1 == 67658
    # puzzle.answer_a = ans1
    ans2 = part2(load(puzzle.input_data))
    assert ans2 == 200158
    # puzzle.answer_b = ans2
