# Advent of Code 2022, Day 19
# (c) blu3r4y

from functools import lru_cache
from math import ceil, comb, prod
from typing import Iterable, List, Tuple

from aocd.models import Puzzle
from funcy import collecting, print_calls, print_durations
from parse import parse
from tqdm import tqdm

ORE, CLA, OBS, GEO = 0, 1, 2, 3

# ore, clay, obsidian, geode tuple
Quadruple = Tuple[int, int, int, int]
Blueprint = Tuple[Quadruple, Quadruple, Quadruple, Quadruple]


class Solver:
    def __init__(self, blueprints: List[Blueprint]):
        self.blueprints: List[Blueprint] = blueprints
        self.active_blueprint: Blueprint = None
        self.active_limits: Quadruple = None

    def solve(self, time_limit: int) -> List[int]:
        results, nstates = [], 0
        with tqdm(unit="blueprint", total=len(self.blueprints)) as pbar:
            for blueprint in self.blueprints:
                self.dfs.cache_clear()

                # the maximum number of robots (excluding geodes)
                # that we are allowed to build in total
                self.active_limits = Solver.robot_limits(blueprint)
                self.active_blueprint = blueprint

                # compute the maximum number of geodes that we can build
                # start at timestamp 1 with 1 ore already in the inventory
                rates, inventory = (1, 0, 0, 0), (1, 0, 0, 0)
                maxgeo = self.dfs(rates, inventory, time_limit - 1)
                results.append(maxgeo)

                # print debug info
                ci = self.dfs.cache_info()
                nstates += ci.hits + ci.misses
                pbar.set_postfix(ngeo=sum(results), nstates=f"{nstates:,d}")
                pbar.update()

        return results

    # this should allocate no more than 12 GB memory
    @lru_cache(maxsize=30_000_000)
    def dfs(self, rates: Quadruple, inventory: Quadruple, t: int) -> int:
        maxgeo = inventory[GEO]

        if t <= 0:  # [prune] out of time
            return maxgeo

        if t == 1:  # [prune] no need to build robots in the last minute
            return maxgeo + rates[GEO]

        # [prune] assuming we only build geode robots from now on,
        # is it even possible to increase the current maximum?
        optgeo = inventory[GEO] + rates[GEO] * t + comb(t, 2)
        if optgeo <= maxgeo:
            return maxgeo

        for robot in self.available_robots(rates):
            # [prune] compute how long we have to wait until we have the
            # required resources and skip to that timestamp already
            # plus one minute to build the robot after that
            costs = self.active_blueprint[robot]
            goals = Solver.subtract_quadruples(costs, inventory)
            dt = Solver.minutes_until_resources(rates, goals) + 1

            dt = max(1, dt)
            if dt > t:  # [prune] not enough time to get there
                continue

            # recurse depth-first
            nrates, ninv = self.step(rates, inventory, robot=robot, t=dt)
            maxgeo = max(maxgeo, self.dfs(nrates, ninv, t - dt))

        return maxgeo

    def available_robots(self, rates: Quadruple) -> Iterable[int]:
        rore, rcla, robs, _ = rates
        if rore > 0 and robs > 0:
            yield GEO
        if rore > 0 and rcla > 0 and robs < self.active_limits[OBS]:
            yield OBS
        if rore > 0 and rcla < self.active_limits[CLA]:
            yield CLA
        if rore > 0 and rore < self.active_limits[ORE]:
            yield ORE

    def step(
        self, rates: Quadruple, inventory: Quadruple, robot: int, t: int = 1
    ) -> Tuple[Quadruple, Quadruple]:
        costs = self.active_blueprint[robot]
        new_inventory, new_rates = [], []

        for j, (iv, rt, ct) in enumerate(zip(inventory, rates, costs)):
            # current items + produced items - consumed items
            new_inventory.append(iv + rt * t - ct)
            new_rates.append(rt + 1 if j == robot else rt)

        return tuple(new_rates), tuple(new_inventory)

    @staticmethod
    def minutes_until_resources(rates: Quadruple, goals: Quadruple) -> int:
        # number of minutes until we have `goal` resources with the given `rates`
        return max(0 if g <= 0 else ceil(g / r) for r, g in zip(rates, goals))

    @staticmethod
    def robot_limits(blueprint: Blueprint) -> Quadruple:
        # number of robots to build until we can build every robot every minute
        return tuple(max(c) for c in zip(*blueprint))

    @staticmethod
    def subtract_quadruples(a: Quadruple, b: Quadruple) -> Quadruple:
        # element-wise subtraction of two quadruples
        return tuple(ai - bi for ai, bi in zip(a, b))


@print_calls
@print_durations(unit="ms")
def part1(blueprints: List[Blueprint]):
    results = Solver(blueprints).solve(24)
    return sum(i * geo for i, geo in enumerate(results, 1))


@print_calls
@print_durations(unit="ms")
def part2(blueprints):
    results = Solver(blueprints[:3]).solve(32)
    return prod(results)


@collecting
def load(data) -> Iterable[Blueprint]:
    for line in data.split("\n"):
        r0, r1, r2, r3, *_ = [ln.strip() for ln in line.split(": ")[1].split(".")]

        pore = parse("Each ore robot costs {:d} ore", r0)
        pcla = parse("Each clay robot costs {:d} ore", r1)
        pobs = parse("Each obsidian robot costs {:d} ore and {:d} clay", r2)
        pgeo = parse("Each geode robot costs {:d} ore and {:d} obsidian", r3)

        ore = (pore[0], 0, 0, 0)
        cla = (pcla[0], 0, 0, 0)
        obs = (pobs[0], pobs[1], 0, 0)
        geo = (pgeo[0], 0, pgeo[1], 0)

        yield (ore, cla, obs, geo)


if __name__ == "__main__":
    puzzle = Puzzle(year=2022, day=19)

    ans1 = part1(load(puzzle.input_data))
    assert ans1 == 1144
    # puzzle.answer_a = ans1

    ans2 = part2(load(puzzle.input_data))
    assert ans2 == 19980
    # puzzle.answer_b = ans2
