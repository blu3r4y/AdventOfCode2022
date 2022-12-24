# Advent of Code 2022, Day 24
# (c) blu3r4y

from collections import defaultdict
from functools import cache
from queue import PriorityQueue
from typing import Dict, Iterable, List, NamedTuple, Tuple

from aocd.models import Puzzle
from funcy import print_calls, print_durations

H, V = 0, 1
UP, DOWN, LEFT, RIGHT = -1j, 1j, -1, 1
WRAP_HV = {UP: V, DOWN: V, LEFT: H, RIGHT: H}

Blizzards = Dict[complex, List[complex]]
State = NamedTuple("State", [("pos", complex), ("steps", int)])


class PuzzleSolver:
    def __init__(
        self,
        blizzards: Blizzards,
        start: complex,
        goal: complex,
        bounds: Tuple[int, int],
    ):
        self.blizzards = blizzards
        self.start = start
        self.goal = goal
        self.bounds = bounds

    def solve(self, backwards: bool = False):
        # shortest path to goal
        start_state = State(self.start, 0)
        goal_state = self.astar_search(start_state)
        if not backwards:
            return goal_state.steps

        # return back to start, then to goal again
        self.start, self.goal = self.goal, self.start
        goal_state = self.astar_search(goal_state)
        self.start, self.goal = self.goal, self.start
        goal_state = self.astar_search(goal_state)

        return goal_state.steps

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
                new_steps = closed[current] + 1
                if succ not in closed or new_steps < closed[succ]:
                    closed[succ] = new_steps
                    estimate = new_steps + self.estimate_remaining_steps(succ)
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
                or (nxt.real < 0 or nxt.real > self.bounds[H] - 1)
                or (nxt.imag < 0 or nxt.imag > self.bounds[V] - 1)
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
                if WRAP_HV[dir] == H:
                    blizzards[
                        complex(
                            real=(pos.real + dir.real * t) % self.bounds[H],
                            imag=pos.imag,
                        )
                    ].append(dir)

                elif WRAP_HV[dir] == V:
                    blizzards[
                        complex(
                            real=pos.real,
                            imag=(pos.imag + dir.imag * t) % self.bounds[V],
                        )
                    ].append(dir)

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
    lines = data.split("\n")
    width, height = len(lines[0]) - 2, len(lines) - 2

    # parse the blizzard positions
    mapping = {"^": UP, "v": DOWN, "<": LEFT, ">": RIGHT}
    for y, line in enumerate(lines[1:-1]):
        for x, cell in enumerate(line[1:-1]):
            if cell != ".":
                blizzards[x + y * 1j].append(mapping[cell])

    # assume start and end positions in the corners
    start, goal = 0 - 1j, (width - 1) + height * 1j

    return PuzzleSolver(blizzards, start, goal, bounds=(width, height))


if __name__ == "__main__":
    puzzle = Puzzle(year=2022, day=24)

    ans1 = part1(load(puzzle.input_data))
    assert ans1 == 262
    # puzzle.answer_a = ans1

    ans2 = part2(load(puzzle.input_data))
    assert ans2 == 785
    # puzzle.answer_b = ans2
