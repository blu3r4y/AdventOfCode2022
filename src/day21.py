# Advent of Code 2022, Day 21
# (c) blu3r4y

from collections import deque, namedtuple
from operator import __add__, __mul__, __sub__, __truediv__

from aocd.models import Puzzle
from funcy import print_calls, print_durations
from parse import parse
from sympy import Integer, Symbol
from sympy.solvers import solve

Primitive = namedtuple("Primitive", ["name", "val"])
Operation = namedtuple("Operation", ["name", "op", "a", "b"])


@print_calls
@print_durations(unit="ms")
def part1(monkeys):
    return int(expand(monkeys, "root"))


@print_calls
@print_durations(unit="ms")
def part2(monkeys, root="root", humn="humn"):
    # make the human primitive a sympy Symbol object
    # and make other primitives into sympy Integer objects
    monkeys[humn] = Primitive(humn, Symbol(humn))
    for key in monkeys:
        if isinstance(monkeys[key], Primitive) and key != humn:
            monkeys[key] = Primitive(key, Integer(monkeys[key].val))

    # grab the left and right hand side of the equation
    left, right = monkeys[root].a, monkeys[root].b

    # expand and solve 'left - right == 0' for humn
    left = expand(monkeys, left)
    right = expand(monkeys, right)
    return solve(left - right, humn)[0]


def expand(monkeys, target="root"):
    fringe = deque(monkeys.values())
    done = dict()

    while fringe:
        monkey = fringe.pop()

        # directly resolve primitive values
        if isinstance(monkey, Primitive):
            done[monkey.name] = monkey.val
            continue

        # resolve operation if both operands are already resolved
        if monkey.a in done and monkey.b in done:
            done[monkey.name] = monkey.op(done[monkey.a], done[monkey.b])
            continue

        # otherwise push back to the fringe, but with the operands first
        fringe.append(monkey)
        if monkey.a not in done:
            fringe.append(monkeys[monkey.a])
        if monkey.b not in done:
            fringe.append(monkeys[monkey.b])

    return done[target]


def load(data):
    operands = {"+": __add__, "-": __sub__, "*": __mul__, "/": __truediv__}
    monkeys = {}
    for line in data.split("\n"):
        name, val = line.split(": ")
        if val.isdigit():
            monkeys[name] = Primitive(name, int(val))
        else:
            a, op, b = parse("{} {} {}", val)
            monkeys[name] = Operation(name, operands[op], a, b)

    return monkeys


if __name__ == "__main__":
    puzzle = Puzzle(year=2022, day=21)

    ans1 = part1(load(puzzle.input_data))
    assert ans1 == 169525884255464
    # puzzle.answer_a = ans1

    ans2 = part2(load(puzzle.input_data))
    assert ans2 == 3247317268284
    # puzzle.answer_b = ans2
