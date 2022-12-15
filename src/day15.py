# Advent of Code 2022, Day 15
# (c) blu3r4y

from collections import namedtuple

from aocd.models import Puzzle
from funcy import collecting, print_calls
from parse import parse
from tqdm import tqdm

# coordinates of the sensor (s) and its beacon (b)
Sensor = namedtuple("Sensor", ["sx", "sy", "bx", "by"])


@print_calls
def part1(sensors, y=2_000_000, pad=2_000_000):
    occupied = get_occupied_positions(sensors)
    radiuses = get_sensor_radiuses(sensors)

    # horizontal bounds for exhaustive scan
    xmin = min(min(r.sx, r.bx) for r in sensors)
    xmax = max(max(r.sx, r.bx) for r in sensors)

    # exhaustive scan of the horizontal line (with padding)
    blocked = 0
    for x in tqdm(range(xmin - pad, xmax + pad)):
        if (x, y) in occupied:
            continue
        if in_any_sensor_range(x, y, sensors, radiuses):
            blocked += 1

    # number of postions that can contain no beacon
    return blocked


@print_calls
def part2(sensors, limit=4_000_000):
    occupied = get_occupied_positions(sensors)
    radiuses = get_sensor_radiuses(sensors)

    # look at pairwise sensor distances
    ireadings = set()
    for i1, r1 in enumerate(sensors):
        for i2, r2 in enumerate(sensors):
            if i1 == i2:
                continue

            # if two sensors are are exactly this far apart
            # they will leave a gap of exactly 1 between them
            dist = abs(r1.sx - r2.sx) + abs(r1.sy - r2.sy)
            if dist == radiuses[i1] + radiuses[i2] + 2:
                ireadings.add(i1)
                ireadings.add(i2)

    ireadings = [sensors[i] for i in ireadings]
    for x, y in all_outlines(ireadings, pad=1):
        # stay within the specified bounds
        if not (0 <= x <= limit and 0 <= y <= limit):
            continue
        if (x, y) in occupied:
            continue

        # the first point that is NOT within the range of ANY sensor
        if not in_any_sensor_range(x, y, sensors, radiuses):
            return x * 4_000_000 + y


def get_occupied_positions(sensors):
    # positions already occupied by beacons or sensors
    beacons = set((r.bx, r.by) for r in sensors)
    sensors = set((r.sx, r.sy) for r in sensors)
    return beacons | sensors


@collecting
def get_sensor_radiuses(sensors):
    # range of each sensor, i.e., manhattan distance to its beacon
    for r in sensors:
        yield abs(r.sx - r.bx) + abs(r.sy - r.by)


def in_any_sensor_range(x, y, sensors, radiuses):
    # check if the point is within the range of any sensor
    for r, limit in zip(sensors, radiuses):
        dist = abs(r.sx - x) + abs(r.sy - y)
        if dist <= limit:
            return True


def all_outlines(sensors, pad=0):
    for r in sensors:
        yield from sensor_outline(r, pad=pad)


def sensor_outline(r, pad=0):
    dx, dy = abs(r.bx - r.sx), abs(r.by - r.sy)
    limit = dx + dy + pad

    # all points on the outline of the sensor, i.e.,
    # those that are exactly at the range of the sensor,
    # plus an optional padding to possibly extend the range
    for y in range(dy + 1 + pad):
        for x in range(dx + 1 + pad):
            mx, my = limit - y, limit - x
            if mx < 0 or my < 0:
                continue

            yield (r.sx + mx, r.sy + y)
            yield (r.sx - mx, r.sy + y)
            yield (r.sx + mx, r.sy - y)
            yield (r.sx - mx, r.sy - y)

            yield (r.sx + x, r.sy + my)
            yield (r.sx - x, r.sy + my)
            yield (r.sx + x, r.sy - my)
            yield (r.sx - x, r.sy - my)


@collecting
def load(data):
    pattern = "Sensor at x={:d}, y={:d}: closest beacon is at x={:d}, y={:d}"
    for line in data.split("\n"):
        yield Sensor(*parse(pattern, line).fixed)


if __name__ == "__main__":
    puzzle = Puzzle(year=2022, day=15)

    ans1 = part1(load(puzzle.input_data))
    assert ans1 == 5809294
    # puzzle.answer_a = ans1

    ans2 = part2(load(puzzle.input_data))
    assert ans2 == 10693731308112
    # puzzle.answer_b = ans2
