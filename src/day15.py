# Advent of Code 2022, Day 15
# (c) blu3r4y

from collections import namedtuple
from itertools import combinations

from aocd.models import Puzzle
from funcy import collecting, print_calls
from parse import parse
from tqdm import tqdm

# coordinates of the sensor (s) and its beacon (b)
RawSensor = namedtuple("RawSensor", ["sx", "sy", "bx", "by"])
Sensor = namedtuple("Sensor", ["sx", "sy", "bx", "by", "radius"])


@print_calls
def part1(sensors, y=2_000_000):
    sensors = process_sensors(sensors)
    occupied = occupied_positions(sensors)

    # horizontal bounds for exhaustive scan
    xmin = min(min(s.sx, s.bx) for s in sensors)
    xmax = max(max(s.sx, s.bx) for s in sensors)
    radmax = max(s.radius for s in sensors)

    # exhaustive scan of the horizontal line
    blocked = 0
    for x in tqdm(range(xmin - radmax, xmax + radmax)):
        if (x, y) in occupied:
            continue
        if in_any_sensor_range(x, y, sensors):
            blocked += 1

    # number of postions that can contain no beacon
    return blocked


@print_calls
def part2(sensors, limit=4_000_000):
    sensors = process_sensors(sensors)
    occupied = occupied_positions(sensors)

    isensors = set()
    for s1, s2 in combinations(sensors, 2):
        # if two sensors are are exactly this far apart
        # they will leave a gap of exactly 1 between them
        dist = abs(s1.sx - s2.sx) + abs(s1.sy - s2.sy)
        if dist == s1.radius + s2.radius + 2:
            isensors.add(s1)
            isensors.add(s2)

    # iterate over remaining sensor borders (start with small radiuses)
    isensors = sorted(isensors, key=lambda s: s.radius)
    for x, y in all_sensor_outlines(isensors, pad=1):
        # stay within the specified bounds
        if not (0 <= x <= limit and 0 <= y <= limit):
            continue
        if (x, y) in occupied:
            continue

        # the first point that is NOT within the range of ANY sensor
        if not in_any_sensor_range(x, y, sensors):
            return x * 4_000_000 + y


@collecting
def process_sensors(sensors):
    for s in sensors:
        # precompute the radius of each sensor
        radius = abs(s.bx - s.sx) + abs(s.by - s.sy)
        yield Sensor(*s, radius)


def occupied_positions(sensors):
    # positions already occupied by beacons or sensors
    beacons = set((s.bx, s.by) for s in sensors)
    sensors = set((s.sx, s.sy) for s in sensors)
    return beacons | sensors


def in_any_sensor_range(x, y, sensors):
    # check if the point is within the range of any sensor
    for sensor in sensors:
        dist = abs(sensor.sx - x) + abs(sensor.sy - y)
        if dist <= sensor.radius:
            return True


def all_sensor_outlines(sensors, pad=0):
    for sensor in sensors:
        yield from sensor_outline(sensor, pad=pad)


def sensor_outline(sensor, pad=0):
    # all points on the outline of the sensor, i.e.,
    # those that are exactly at the range of the sensor,
    # plus an optional padding to possibly extend the range
    limit = sensor.radius + pad
    for d in range(limit):
        yield (sensor.sx + d, sensor.sy + limit - d)
        yield (sensor.sx - d, sensor.sy + limit - d)
        yield (sensor.sx + d, sensor.sy - limit + d)
        yield (sensor.sx - d, sensor.sy - limit + d)


@collecting
def load(data):
    pattern = "Sensor at x={:d}, y={:d}: closest beacon is at x={:d}, y={:d}"
    for line in data.split("\n"):
        yield RawSensor(*parse(pattern, line).fixed)


if __name__ == "__main__":
    puzzle = Puzzle(year=2022, day=15)

    ans1 = part1(load(puzzle.input_data))
    assert ans1 == 5809294
    # puzzle.answer_a = ans1

    ans2 = part2(load(puzzle.input_data))
    assert ans2 == 10693731308112
    # puzzle.answer_b = ans2
