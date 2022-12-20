# Advent of Code 2022, Day 20
# (c) blu3r4y

from aocd.models import Puzzle
from funcy import first, lmap, print_calls, print_durations


@print_calls
@print_durations(unit="ms")
def part1(nums):
    return solve(nums)


@print_calls
@print_durations(unit="ms")
def part2(nums, key=811589153):
    nums = [num * key for num in nums]
    return solve(nums, nrepeat=10)


def solve(nums, nrepeat=1):
    # add index to each number to make them unique
    nums = list(enumerate(nums))
    orgs = nums.copy()
    size = len(nums)

    for _ in range(nrepeat):
        for i, num in orgs:
            # find this number again and compute new index
            jold = nums.index((i, num))
            jnew = (num + jold) % (size - 1)
            # remove and reinsert at new index
            nums.pop(jold)
            nums.insert(jnew, (i, num))

    # find the index of the first zero, after mixing
    zero = first(i for i, (_, num) in enumerate(nums) if num == 0)

    # the sum of numbers at the indices 1000, 2000, 3000 after mixing
    n1000 = nums[(zero + 1000) % size][1]
    n2000 = nums[(zero + 2000) % size][1]
    n3000 = nums[(zero + 3000) % size][1]
    return n1000 + n2000 + n3000


def load(data):
    return lmap(int, data.splitlines())


if __name__ == "__main__":
    puzzle = Puzzle(year=2022, day=20)

    ans1 = part1(load(puzzle.input_data))
    assert ans1 == 15297
    # puzzle.answer_a = ans1

    ans2 = part2(load(puzzle.input_data))
    assert ans2 == 2897373276210
    # puzzle.answer_b = ans2
