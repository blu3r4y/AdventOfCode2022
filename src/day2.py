# Advent of Code 2022, Day 2
# (c) blu3r4y

from aocd.models import Puzzle
from funcy import collecting, print_calls

ROCK, PAPER, SCISSORS = 1, 2, 3
LOSE_X, DRAW_Y, WIN_Z = 1, 2, 3

SYMBOLS = {
    "A": ROCK,
    "B": PAPER,
    "C": SCISSORS,
    "X": ROCK,
    "Y": PAPER,
    "Z": SCISSORS,
}

MOVE_LOSE = {ROCK: SCISSORS, PAPER: ROCK, SCISSORS: PAPER}
MOVE_DRAW = {ROCK: ROCK, PAPER: PAPER, SCISSORS: SCISSORS}
MOVE_WIN = {ROCK: PAPER, PAPER: SCISSORS, SCISSORS: ROCK}


@print_calls
def part1(data):
    total = 0
    for opponent, me in data:
        total += game_result(me, opponent) + me

    return total


@print_calls
def part2(data):
    total = 0
    for opponent, outcome in data:
        me = move_for_outcome(outcome, opponent)
        total += game_result(me, opponent) + me

    return total


@collecting
def load(data):
    for line in data.split("\n"):
        a, b = line.split()
        yield SYMBOLS[a], SYMBOLS[b]


def game_result(me, opponent):
    if me == opponent:
        return 3
    elif opponent == ROCK and me == PAPER:
        return 6
    elif opponent == PAPER and me == SCISSORS:
        return 6
    elif opponent == SCISSORS and me == ROCK:
        return 6
    else:
        return 0


def move_for_outcome(outcome, opponent):
    if outcome == LOSE_X:
        return MOVE_LOSE[opponent]
    elif outcome == DRAW_Y:
        return MOVE_DRAW[opponent]
    elif outcome == WIN_Z:
        return MOVE_WIN[opponent]


if __name__ == "__main__":
    puzzle = Puzzle(year=2022, day=2)

    ans1 = part1(load(puzzle.input_data))
    assert ans1 == 9759
    # puzzle.answer_a = ans1
    ans2 = part2(load(puzzle.input_data))
    assert ans2 == 12429
    # puzzle.answer_b = ans2
