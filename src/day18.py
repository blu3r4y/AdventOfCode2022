# Advent of Code 2022, Day 18
# (c) blu3r4y

from aocd.models import Puzzle
from funcy import collecting, print_calls, print_durations


@print_calls
@print_durations(unit="ms")
def part1(lava):
    return surface_area(lava)


@print_calls
@print_durations(unit="ms")
def part2(lava):
    # bounding box with 1 extra padding layer to fit the water
    xs, ys, zs = zip(*lava)
    xmin, xmax = min(xs) - 1, max(xs) + 1
    ymin, ymax = min(ys) - 1, max(ys) + 1
    zmin, zmax = min(zs) - 1, max(zs) + 1

    water = set()
    lava = set(lava)
    fringe = {(xmin, ymin, zmin)}

    # flood fill the water around the lava
    while fringe:
        xyz = fringe.pop()
        for adj in adjacent(xyz):
            ax, ay, az = adj
            if (
                (xmin <= ax <= xmax and ymin <= ay <= ymax and zmin <= az <= zmax)
                and adj not in water
                and adj not in lava
            ):
                fringe.add(adj)
                water.add(adj)

    # surface area of our bounding box
    dx, dy, dz = xmax - xmin + 1, ymax - ymin + 1, zmax - zmin + 1
    bb_surface = dx * dy * 2 + dx * dz * 2 + dy * dz * 2

    return surface_area(water) - bb_surface


def surface_area(lava):
    surface = 0
    for xyz in lava:
        # add the number of sides, subtracted by the number of adjacent cubes
        nadj = sum(1 if adj in lava else 0 for adj in adjacent(xyz))
        surface += 6 - nadj

    return surface


def adjacent(xyz):
    # 6 adjacent cubes, no diagonals
    x, y, z = xyz
    return {
        (x - 1, y, z),
        (x + 1, y, z),
        (x, y - 1, z),
        (x, y + 1, z),
        (x, y, z - 1),
        (x, y, z + 1),
    }


@collecting
def load(data):
    for line in data.split("\n"):
        yield tuple(map(int, line.split(",")))


if __name__ == "__main__":
    puzzle = Puzzle(year=2022, day=18)

    ans1 = part1(load(puzzle.input_data))
    assert ans1 == 3500
    # puzzle.answer_a = ans1

    ans2 = part2(load(puzzle.input_data))
    assert ans2 == 2048
    # puzzle.answer_b = ans2
