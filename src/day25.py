# Advent of Code 2022, Day 25
# (c) blu3r4y

from aocd.models import Puzzle
from funcy import print_calls, print_durations


@print_calls
@print_durations(unit="ms")
def part1(nums):
    return dec2snafu(sum(map(snafu2dec, nums)))


def dec2snafu(dec):
    bits = []
    while dec > 0:
        dec, rem = divmod(dec, 5)
        bits.append(rem)

    # respect negative one (1) and negative two (2)
    stack, carry = [], 0
    for bit in bits:
        bit += carry

        if bit == 3:
            stack.append("=")
            carry = 1
        elif bit == 4:
            stack.append("-")
            carry = 1
        elif bit == 5:
            stack.append("0")
            carry = 1
        else:
            stack.append(str(bit))
            carry = 0

    # still a carry left?
    if carry > 0:
        stack.append(str(carry))

    result = "".join(reversed(stack))
    return result


def snafu2dec(snafu):
    result = 0
    for i, bit in enumerate(reversed(snafu)):
        bit = bit.replace("-", "-1").replace("=", "-2")
        result += int(bit) * 5**i

    return result


def load(data):
    return data.split("\n")


if __name__ == "__main__":
    puzzle = Puzzle(year=2022, day=25)

    ans1 = part1(load(puzzle.input_data))
    assert ans1 == "2-1=10=1=1==2-1=-221"
    # puzzle.answer_a = ans1
