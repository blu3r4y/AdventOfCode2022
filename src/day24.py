# Advent of Code 2022, Day 24
# (c) blu3r4y

from collections import defaultdict
from functools import cache
from queue import PriorityQueue
from typing import Dict, Iterable, List, NamedTuple

from aocd.models import Puzzle
from funcy import print_calls, print_durations

UP, DOWN, LEFT, RIGHT = -1j, 1j, -1, 1

Blizzards = Dict[complex, List[complex]]
State = NamedTuple("State", [("pos", complex), ("steps", int)])


class PuzzleSolver:
    def __init__(
        self,
        blizzards: Blizzards,
        start: complex,
        goal: complex,
        width: int,
        height: int,
    ):
        self.blizzards = blizzards
        self.start = start
        self.goal = goal
        self.width = width
        self.height = height

    def solve(self, backwards: bool = False):
        # shortest path to goal
        state = State(self.start, 0)
        state = self.astar_search(state)
        if not backwards:
            return state.steps

        # return back to start, then to goal again
        self.start, self.goal = self.goal, self.start
        state = self.astar_search(state)
        self.start, self.goal = self.goal, self.start
        state = self.astar_search(state)

        return state.steps

    def astar_search(self, start: State):
        openpq = PriorityQueue()
        openpq.put((0, 0, start))
        closed = {start: 0}
        tiebreaker = 1
        goal = None

        while not openpq.empty():
            _, _, current = openpq.get()
            if current.pos == self.goal:
                goal = current
                break

            for succ in self.successor_states(current):
                if succ not in closed or succ.steps < closed[succ]:
                    closed[succ] = succ.steps
                    estimate = succ.steps + self.estimate_remaining_steps(succ)
                    openpq.put((estimate, tiebreaker, succ))
                    tiebreaker += 1

        return goal

    def estimate_remaining_steps(self, state: State) -> int:
        # manhattan distance from pos to goal
        a, b = self.goal, state.pos
        return int(abs(a.imag - b.imag) + abs(a.real - b.real))

    def successor_states(self, state: State) -> Iterable[State]:
        tnext = state.steps + 1
        blizzards = self.blizzards_map(tnext)

        for dir in [DOWN, RIGHT, LEFT, UP]:
            nxt = state.pos + dir

            # already at the goal?
            if nxt == self.goal:
                yield State(nxt, tnext)
                return

            # avoid blizzards and out of bounds moves
            if (
                nxt in blizzards
                or (nxt.real < 0 or nxt.real > self.width - 1)
                or (nxt.imag < 0 or nxt.imag > self.height - 1)
            ):
                continue

            yield State(nxt, tnext)

        # is it safe to stay here?
        if state.pos not in blizzards:
            yield State(state.pos, tnext)

    @cache
    def blizzards_map(self, t) -> Blizzards:
        blizzards = defaultdict(list)

        for pos, dirs in self.blizzards.items():
            for dir in dirs:
                npos = complex(
                    real=(pos.real + dir.real * t) % self.width,
                    imag=(pos.imag + dir.imag * t) % self.height,
                )
                blizzards[npos].append(dir)

        # the blizzard map can be precomputed for each time step
        # and memoized because it will never change for a given time step
        return blizzards


@print_calls
@print_durations(unit="ms")
def part1(solver: PuzzleSolver):
    return solver.solve()


@print_calls
@print_durations(unit="ms")
def part2(solver: PuzzleSolver):
    return solver.solve(backwards=True)


def load(data) -> PuzzleSolver:
    blizzards = defaultdict(list)
    lines = data.splitlines()
    width, height = len(lines[0]) - 2, len(lines) - 2

    # parse the blizzard positions
    mapping = {"^": UP, "v": DOWN, "<": LEFT, ">": RIGHT}
    for y, line in enumerate(lines[1:-1]):
        for x, cell in enumerate(line[1:-1]):
            if cell != ".":
                blizzards[x + y * 1j].append(mapping[cell])

    # assume start and end positions in the corners
    start, goal = 0 - 1j, (width - 1) + height * 1j

    return PuzzleSolver(blizzards, start, goal, width, height)


if __name__ == "__main__":
    puzzle = Puzzle(year=2022, day=24)

    ans1 = part1(load(puzzle.input_data))
    assert ans1 == 262
    # puzzle.answer_a = ans1

    ans2 = part2(load(puzzle.input_data))
    assert ans2 == 785
    # puzzle.answer_b = ans2
