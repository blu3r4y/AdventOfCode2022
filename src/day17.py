# Advent of Code 2022, Day 17
# (c) blu3r4y

from aocd.models import Puzzle
from funcy import print_calls

WIDTH = 7
LEFT, RIGHT = -1, 1
EMPTY, MOVING, SOLID = ".", "@", "#"
EMPTY_LINE = [EMPTY] * WIDTH
SOLID_LINE = [SOLID] * WIDTH
ROCKS = [
    ["####"],
    [".#.", "###", ".#."],
    ["###", "..#", "..#"],
    ["#", "#", "#", "#"],
    ["##", "##"],
]


@print_calls
def part1(jets):
    return solve(jets, limit=2022)


@print_calls
def part2(jets):
    return solve(jets, limit=1000000000000)


def solve(jets, limit):
    # an empty tower with no rock placed
    tower, height, itop = [], 0, -1
    # number of rocks and jet and rock cycle counters
    nrocks, ijet, irock = 0, 0, 0
    # memorize towers to avoid cycles
    known_towers = {}

    # as long as jets are available
    while nrocks < limit:

        # spawn a new rock
        itop = spawn_rock(tower, ROCKS[irock], itop)
        irock = (irock + 1) % len(ROCKS)

        # repeat jet-pushes and down-moves until the rock is solid
        is_moving = True
        while is_moving:
            push_rock(tower, itop, jets[ijet])
            ijet = (ijet + 1) % len(jets)
            itop, is_moving = down_rock(tower, itop)

        nrocks += 1
        itop = tower_height(tower) - 1

        ## cycle detection
        ###################

        # possibly shrink the tower and update indexes
        delta, tower = shrink_tower(tower)
        itop -= delta
        height += delta

        # memorize the tower
        thash = pack_tower(tower, irock, ijet)
        if not thash in known_towers:
            known_towers[thash] = (height, nrocks)
            continue

        # we found a circle! what was the difference?
        theight, trocks = known_towers[thash]
        dheight, drocks = height - theight, nrocks - trocks

        # stack up the difference as much as we can
        nstacks = (limit - nrocks) // drocks
        nrocks += nstacks * drocks
        height += nstacks * dheight

    # don't forget the height of the last active tower
    height += itop + 1
    return height


def spawn_rock(tower, rock, itop):
    itop = itop + 3 + len(rock)
    expand_tower(tower, itop + 1)
    for r, row in enumerate(reversed(rock)):
        for c, col in enumerate(row):
            if col == SOLID:
                tower[itop - r][c + 2] = MOVING

    # spawn position
    return itop


def push_rock(tower, itop, direction):
    update = []

    i = itop
    while i >= 0:
        try:

            # check if we can move in that direction
            # or raise a ValueError
            check = direction + (
                WIDTH - 1 - tower[i][::-1].index(MOVING)
                if direction == RIGHT
                else tower[i].index(MOVING)
            )

            if check < 0 or check >= WIDTH or tower[i][check] == SOLID:
                return  # rock is blocked, push not possible

            # prepare the line updates
            line = tower[i].copy()
            iterator = reversed(range(WIDTH)) if direction == RIGHT else range(WIDTH)
            for j in iterator:
                if tower[i][j] == MOVING:
                    line[j] = EMPTY
                    line[j + direction] = MOVING
            update.append(line)

            i -= 1  # move down

        except ValueError:
            break  # no more moving rocks

    # update the tower with the moved lines
    for i, line in enumerate(update):
        tower[itop - i] = line


def down_rock(tower, itop):
    i = itop

    while i > 0:
        has_rock_line = False

        # just check if we can move down
        for u, d in zip(tower[i], tower[i - 1]):
            if u == MOVING:
                has_rock_line = True
            if u == MOVING and d == SOLID:
                # rock is blocked, can not move down, stop here
                stop_rock(tower, itop)
                return itop, False

        # no more rocks on this line
        if not has_rock_line:
            break

        i -= 1  # move down

    # we hit the bottom, stop here
    if MOVING in tower[0]:
        stop_rock(tower, itop)
        return itop, False

    # actually move down (in-place)
    while i < itop:
        for j, (d, u) in enumerate(zip(tower[i], tower[i + 1])):
            if u == MOVING:
                tower[i][j] = MOVING
                tower[i + 1][j] = EMPTY

        i += 1  # move up

    # successfully moved the rock one down
    return itop - 1, True


def stop_rock(tower, itop):
    i = itop
    while i >= 0:
        solidified = False

        # convert moving rocks to solid rocks (in-place)
        for r in range(WIDTH):
            if tower[i][r] == MOVING:
                tower[i][r] = SOLID
                solidified = True

        # no more moving rocks on that line
        if not solidified:
            return

        i -= 1  # move down


def shrink_tower(tower):
    cutoff, pre = len(tower), [EMPTY]
    for i, row in enumerate(reversed(tower)):

        # the cutoff point is the first non-empty line
        if not cutoff and row != EMPTY_LINE:
            cutoff = len(tower) - i - 1

        # we split below the first truly solid line or one
        # that is solid "together with the previous line", e.g.
        # => pre .#.#.#.
        # => row #.#.#.#
        if all(a == SOLID or b == SOLID for a, b in zip(row, pre)):
            height = len(tower) - i
            return height, tower[height : cutoff + 1]

        pre = row

    return 0, tower[: cutoff + 1]


def tower_height(tower):
    for i, row in enumerate(reversed(tower)):
        if SOLID in row:
            return len(tower) - i

    return 0


def expand_tower(tower, size):
    while len(tower) < size:
        tower.append(EMPTY_LINE.copy())


def pack_tower(tower, irock, ijet):
    # packs the tower and cycle indexes into a hashable string
    return str(irock) + "\n" + str(ijet) + "\n" + "\n".join(["".join(t) for t in tower])


# def print_tower(tower):
#     for i, row in enumerate(reversed(tower)):
#         print(f"{len(tower) - i:3d} {''.join(row)}")
#     print()


def load(data):
    return [RIGHT if ch == ">" else LEFT for ch in data]


if __name__ == "__main__":
    puzzle = Puzzle(year=2022, day=17)

    ans1 = part1(load(puzzle.input_data))
    assert ans1 == 3163
    # puzzle.answer_a = ans1

    ans2 = part2(load(puzzle.input_data))
    assert ans2 == 1560932944615
    # puzzle.answer_b = ans2
