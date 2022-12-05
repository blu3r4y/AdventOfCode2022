# Advent of Code 2022, Day 5
# (c) blu3r4y

from collections import deque, namedtuple

from aocd.models import Puzzle
from funcy import print_calls
from parse import parse

Instruction = namedtuple("Ins", ["n", "start", "end"])


def solve(data, reverse=False):
    crates, instructions = data
    for ins in instructions:
        stash = []
        for _ in range(ins.n):
            item = crates[ins.start].pop()
            stash.append(item)
        if reverse:
            stash.reverse()
        crates[ins.end].extend(stash)

    # solution string
    return "".join([crates[k][-1] for k in crates.keys()])


@print_calls
def part1(data):
    return solve(data)


@print_calls
def part2(data):
    return solve(data, reverse=True)


def load(data):
    lines = data.split("\n")

    ncrates = len(lines[0]) // 4 + 1
    nheight = lines.index("") - 1

    # parse crate stacks
    crates = {i: deque() for i in range(1, ncrates + 1)}
    for line in lines[0:nheight]:
        for ci, i in enumerate(range(ncrates)):
            item = line[i * 4 : i * 4 + 4].strip()[1:2]
            if item:
                crates[ci + 1].insert(0, item)

    # parse move instructions
    instructions = []
    for line in lines[nheight + 2 :]:
        ins = Instruction(*parse("move {:d} from {:d} to {:d}", line).fixed)
        instructions.append(ins)

    return crates, instructions


if __name__ == "__main__":
    puzzle = Puzzle(year=2022, day=5)

    ans1 = part1(load(puzzle.input_data))
    assert ans1 == "BWNCQRMDB"
    # puzzle.answer_a = ans1
    ans2 = part2(load(puzzle.input_data))
    assert ans2 == "NHWZCBNBF"
    # puzzle.answer_b = ans2
