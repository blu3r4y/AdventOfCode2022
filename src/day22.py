# Advent of Code 2022, Day 22
# (c) blu3r4y

import re
from dataclasses import dataclass, field
from typing import Dict, List, Literal, Tuple

from aocd.models import Puzzle
from funcy import print_calls, print_durations

RIGHT, LEFT, UP, DOWN = 1, -1, -1j, 1j
TURN_RIGHT, TURN_LEFT = 1j, -1j

SYMBOL_FREE, SYMBOL_WALL = ".", "#"
SYMBOL_RIGHT, SYMBOL_LEFT = "R", "L"
DIRECTION_FACTOR = {RIGHT: 0, DOWN: 1, LEFT: 2, UP: 3}

EDGES = {
    ((0, 2), RIGHT): ((1, 2), LEFT, 0),
    ((0, 2), LEFT): ((1, 0), LEFT, 1),  # flip
    ((0, 2), UP): ((1, 1), LEFT, 0),
    ((0, 2), DOWN): ((0, 3), UP, 0),
    #
    ((0, 3), RIGHT): ((1, 2), DOWN, 0),
    ((0, 3), LEFT): ((1, 0), UP, 0),
    ((0, 3), UP): ((0, 2), DOWN, 0),
    ((0, 3), DOWN): ((2, 0), UP, 0),
    #
    ((1, 0), RIGHT): ((2, 0), LEFT, 0),
    ((1, 0), LEFT): ((0, 2), LEFT, 1),  # flip
    ((1, 0), UP): ((0, 3), LEFT, 0),
    ((1, 0), DOWN): ((1, 1), UP, 0),
    #
    ((1, 1), RIGHT): ((2, 0), DOWN, 0),
    ((1, 1), LEFT): ((0, 2), UP, 0),
    ((1, 1), UP): ((1, 0), DOWN, 0),
    ((1, 1), DOWN): ((1, 2), UP, 0),
    #
    ((1, 2), RIGHT): ((2, 0), RIGHT, 1),  # flip
    ((1, 2), LEFT): ((0, 2), RIGHT, 0),
    ((1, 2), UP): ((1, 1), DOWN, 0),
    ((1, 2), DOWN): ((0, 3), RIGHT, 0),
    #
    ((2, 0), RIGHT): ((1, 2), RIGHT, 1),  # flip
    ((2, 0), LEFT): ((1, 0), RIGHT, 0),
    ((2, 0), UP): ((0, 3), DOWN, 0),
    ((2, 0), DOWN): ((1, 1), RIGHT, 0),
}


@dataclass
class Cube:
    # maps coordinates to symbols
    coords: Dict[complex, Literal[".", "#"]]
    # maps coordinates to the (x, y) face they belong to
    faces: Dict[complex, Tuple[int, int]] = field(init=False)
    # movement sequence (turns and steps)
    sequence: List[complex | int]
    # height of the grid
    height: int
    # width of the grid
    width: int
    # width and height of a single face
    tile_size: int
    # starting point in the grid
    start: complex

    def __post_init__(self):
        self.faces = self._assign_faces()

    def _assign_faces(self):
        faces = {}
        for y in range(1, self.height + 1):
            yindex = (y - 1) // self.tile_size
            for x in range(1, self.width + 1):
                xindex = (x - 1) // self.tile_size

                # map coordinates to the face they belong to
                if (pos := x + y * 1j) in self.coords:
                    face = (xindex, yindex)
                    faces[pos] = face

        return faces


@print_calls
@print_durations(unit="ms")
def part1(cube: Cube):
    curr, dir = walk(cube, wrap_func=wrap2d)
    return int(1000 * curr.imag + 4 * curr.real + DIRECTION_FACTOR[dir])


@print_calls
@print_durations(unit="ms")
def part2(cube: Cube):

    curr, dir = walk(cube, wrap_func=wrap3d)
    return int(1000 * curr.imag + 4 * curr.real + DIRECTION_FACTOR[dir])


def walk(cube: Cube, wrap_func: callable):
    # start position facing right
    pos, dir = cube.start, RIGHT

    for move in cube.sequence:
        # turn right or left
        if isinstance(move, complex):
            dir *= move
            continue

        # move forward step-by-step
        backup = pos, dir
        for _ in range(move):
            pos += dir

            # possibly wrap around
            if pos not in cube.coords:
                pos, dir = wrap_func(pos, dir, cube)

            # revert move and abort if we hit a wall
            if cube.coords[pos] == SYMBOL_WALL:
                pos, dir = backup
                break

            backup = pos, dir

    return pos, dir


def wrap2d(pos: complex, dir: complex, cube: Cube):
    assert pos not in cube.coords

    # wrap around in direction
    if dir == RIGHT:
        pos = 1 + pos.imag * 1j
    elif dir == LEFT:
        pos = cube.width + pos.imag * 1j
    elif dir == UP:
        pos = pos.real + cube.height * 1j
    elif dir == DOWN:
        pos = pos.real + 1j

    # line search next valid point
    while pos not in cube.coords:
        pos += dir
    return pos, dir


def wrap3d(pos: complex, dir: complex, cube: Cube):
    assert pos not in cube.coords

    # revert last move, find face, and relative position in face
    pos = pos - dir
    rpos = complex(
        real=(pos.real - 1) % cube.tile_size + 1,
        imag=(pos.imag - 1) % cube.tile_size + 1,
    )

    # which face shall we wrap around to next?
    nface, ndir, nflip = EDGES[cube.faces[pos], dir]

    # possibly flip our relative coordinates
    if nflip:
        rpos = complex(
            real=cube.tile_size - rpos.real + 1,  ##
            imag=cube.tile_size - rpos.imag + 1,
        )

    # how far away from the corner are we on our edge
    edgedist = 0
    if dir == LEFT or dir == RIGHT:
        edgedist = rpos.imag - 1
    elif dir == UP or dir == DOWN:
        edgedist = rpos.real - 1

    # initialize the upper left corner on the new face
    # and move relative alonge that edge
    bxy = (1 + 1j) + nface[0] * cube.tile_size + nface[1] * cube.tile_size * 1j
    if ndir == LEFT:
        bxy += edgedist * 1j
    elif ndir == RIGHT:
        bxy += edgedist * 1j + (cube.tile_size - 1)
    elif ndir == UP:
        bxy += edgedist
    elif ndir == DOWN:
        bxy += edgedist + (cube.tile_size - 1) * 1j

    # move opposite to the direction that we entered the face
    ndir = -ndir

    return bxy, ndir


def load(data, tile_size=50):
    card, phrase = data.split("\n\n")

    # prepare map processing
    card = card.split("\n")
    height, width = len(card), max(map(len, card))
    width = max(map(len, card))
    coords, start = {}, None

    # read map coordinates
    for y, row in enumerate(card, 1):
        row = row.ljust(width, " ")
        for x, symbol in enumerate(row, 1):
            if symbol == SYMBOL_WALL or symbol == SYMBOL_FREE:
                pos = x + y * 1j
                coords[pos] = symbol
                if start is None:
                    start = pos

    # read and transform move sequence
    sequence = []
    for ch in re.split("([LR])", phrase):
        if ch == "R":
            sequence.append(TURN_RIGHT)
        elif ch == "L":
            sequence.append(TURN_LEFT)
        else:
            assert ch.isnumeric()
            sequence.append(int(ch))

    return Cube(
        coords=coords,
        sequence=sequence,
        height=height,
        width=width,
        start=start,
        tile_size=tile_size,
    )


if __name__ == "__main__":
    puzzle = Puzzle(year=2022, day=22)

    ans1 = part1(load(puzzle.input_data))
    assert ans1 == 159034
    puzzle.answer_a = ans1

    ans2 = part2(load(puzzle.input_data))
    assert ans2 == 147245
    puzzle.answer_b = ans2
