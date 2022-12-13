# Advent of Code 2022, Day 13
# (c) blu3r4y

from collections import namedtuple
from functools import cmp_to_key

from aocd.models import Puzzle
from funcy import collecting, lcat, print_calls

Pair = namedtuple("Pair", ["left", "right"])


@print_calls
def part1(pairs):
    total = 0
    for i, pair in enumerate(pairs, 1):
        if ordered(pair.left, pair.right):
            total += i

    # sum of the indices of the ordered pairs
    return total


@print_calls
def part2(pairs):
    # flatten packets and add divider packets
    packets = lcat(pairs) + [[[2]], [[6]]]

    # sort packets by their order
    key_func = cmp_to_key(lambda l, r: 1 if ordered(l, r) else -1)
    packets = sorted(packets, key=key_func, reverse=True)

    # return the product of the indices of the divider packets
    return (packets.index([[2]]) + 1) * (packets.index([[6]]) + 1)


def ordered(left, right):
    assert isinstance(left, list) and isinstance(right, list)

    # compare list elements with each other
    for l, r in zip(left, right):
        lint, rint = isinstance(l, int), isinstance(r, int)
        llist, rlist = isinstance(l, list), isinstance(r, list)

        # if only one is a int, convert the other to a list
        if lint ^ rint:
            l = l if llist else [l]
            r = r if rlist else [r]
            lint, rint, llist, rlist = False, False, True, True

        # if both are ints, the lower must be on the left
        if lint and rint and l != r:
            return l < r

        # if both are lists, the left must be ordered
        if llist and rlist and (res := ordered(l, r)) is not None:
            return res

    # equal list lengths, no decision could be made
    if len(left) == len(right):
        return None

    # if lists are of unequal length, the left must be shorter
    return len(left) < len(right)


@collecting
def load(data):
    for pairs in data.split("\n\n"):
        l, r = pairs.split("\n")
        l, r = eval(l), eval(r)
        yield Pair(l, r)


if __name__ == "__main__":
    puzzle = Puzzle(year=2022, day=13)

    ans1 = part1(load(puzzle.input_data))
    assert ans1 == 6086
    # puzzle.answer_a = ans1

    ans2 = part2(load(puzzle.input_data))
    assert ans2 == 27930
    # puzzle.answer_b = ans2
