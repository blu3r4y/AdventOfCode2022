# Advent of Code 2022, Day 11
# (c) blu3r4y

import math
from collections import deque, namedtuple
from operator import __add__, __mul__
from typing import List, Optional

from aocd.models import Puzzle
from funcy import collecting, print_calls
from parse import parse

Monkey = namedtuple("Monkey", ["no", "start", "op", "test", "iftrue", "iffalse"])


@print_calls
def part1(monkeys):
    return solve(monkeys, nrounds=20, div=3)


@print_calls
def part2(monkeys):
    lcm = math.lcm(*[monkey.test for monkey in monkeys])
    return solve(monkeys, nrounds=10_000, mod=lcm)


def solve(monkeys: List[Monkey], nrounds: int, div: int = 1, mod: Optional[int] = None):
    counts = [0] * len(monkeys)

    for _ in range(nrounds):
        for i in range(len(monkeys)):

            monkey = monkeys[i]
            while monkey.start:
                # get and inspect monkey
                item = monkey.start.popleft()
                item = inspect(item, monkey.op)
                counts[monkey.no] += 1

                # divide and possibly take modulo
                item = item // div
                if mod:
                    item = item % mod

                # throw to next monkey
                test = item % monkey.test == 0
                target = monkey.iftrue if test else monkey.iffalse
                monkeys[target].start.append(item)

    # multiple the largest two numbers
    l1, l2 = sorted(counts, reverse=True)[:2]
    return l1 * l2


def inspect(item, op):
    operator, num = op
    if isinstance(num, int):
        return operator(item, num)
    else:
        return operator(item, item)


@collecting
def load(data):
    monkeys = data.split("\n\n")
    for monkey in monkeys:
        no, start, op, test, iftrue, iffalse = monkey.split("\n")
        no = parse("Monkey {:d}:", no)[0]
        start = parse("  Starting items: {}", start)[0]
        op = parse("  Operation: new = old {} {:w}", op)
        test = parse("  Test: divisible by {:d}", test)[0]
        iftrue = parse("    If true: throw to monkey {:d}", iftrue)[0]
        iffalse = parse("    If false: throw to monkey {:d}", iffalse)[0]

        # fixup start list
        start = deque(map(int, start.split(", ")))

        # fixup operation
        op1 = __add__ if op[0] == "+" else __mul__
        op2 = int(op[1]) if op[1].isdigit() else op[1]
        op = (op1, op2)

        yield Monkey(no, start, op, test, iftrue, iffalse)


if __name__ == "__main__":
    puzzle = Puzzle(year=2022, day=11)

    ans1 = part1(load(puzzle.input_data))
    assert ans1 == 108240
    # puzzle.answer_a = ans1

    ans2 = part2(load(puzzle.input_data))
    assert ans2 == 25712998901
    # puzzle.answer_b = ans2
