# Advent of Code 2022, Day 23
# (c) blu3r4y

from collections import defaultdict

from aocd.models import Puzzle
from funcy import count, print_calls, print_durations

N, NE, E, SE, S, SW, W, NW = -1j, 1 - 1j, 1, 1 + 1j, 1j, 1j - 1, -1, -1 - 1j
DIRECTIONS = [N, NE, E, SE, S, SW, W, NW]
FREE, ELF = 0, 1


@print_calls
@print_durations(unit="ms")
def part1(grid):
    # simulate a maximum of 10 rounds
    simulate(grid, round_limit=10)

    # bounding box around elves
    elves = [pos for pos, cell in grid.items() if cell == ELF]
    xs, ys = [int(e.real) for e in elves], [int(e.imag) for e in elves]
    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)

    # count free cells
    nfree = 0
    for y in range(ymin, ymax + 1):
        for x in range(xmin, xmax + 1):
            cell = grid.get(x + y * 1j, FREE)
            nfree += cell == FREE

    return nfree


@print_calls
@print_durations(unit="ms")
def part2(grid):
    # round number until no more elves can move
    return simulate(grid, round_limit=float("inf "))


def simulate(grid, round_limit):
    # consideration and proposal order
    propose, index = [N, S, W, E], 0
    consider = [
        lambda e: free(grid, e, N) and free(grid, e, NE) and free(grid, e, NW),
        lambda e: free(grid, e, S) and free(grid, e, SE) and free(grid, e, SW),
        lambda e: free(grid, e, W) and free(grid, e, NW) and free(grid, e, SW),
        lambda e: free(grid, e, E) and free(grid, e, NE) and free(grid, e, SE),
    ]

    for round in count():

        # find all the elves ready to move, i.e. still have elves around them
        unblocked_elves = []
        for elf in [pos for pos, cell in grid.items() if cell == ELF]:
            if any(n == ELF for n in neighbors(grid, elf)):
                unblocked_elves.append(elf)

        # no more elves to move or round limit reached
        if len(unblocked_elves) == 0 or round >= round_limit:
            return round + 1

        # make move proposals
        moves, noverlaps = [], defaultdict(int)
        for elf in unblocked_elves:
            move = None

            for round in range(index, index + 4):
                round = round % 4
                if consider[round](elf):
                    move = propose[round]
                    break

            if move is not None:
                moves.append((elf, move))
                noverlaps[elf + move] += 1

        # perform moves
        for elf, move in moves:
            if noverlaps[elf + move] > 1:
                continue
            grid[elf] = FREE
            grid[elf + move] = ELF

        # rotate consideration order
        index = (index + 1) % 4


def free(grid, pos, d):
    return grid.get(pos + d, FREE) == FREE


def neighbors(grid, pos):
    return (grid.get(pos + d, FREE) for d in DIRECTIONS)


def load(data):
    grid = {}
    for y, row in enumerate(data.split("\n")):
        for x, cell in enumerate(row):
            grid[x + y * 1j] = ELF if cell == "#" else FREE
    return grid


if __name__ == "__main__":
    puzzle = Puzzle(year=2022, day=23)

    ans1 = part1(load(puzzle.input_data))
    assert ans1 == 4049
    # puzzle.answer_a = ans1

    ans2 = part2(load(puzzle.input_data))
    assert ans2 == 1021
    # puzzle.answer_b = ans2
