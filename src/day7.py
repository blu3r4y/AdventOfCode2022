# Advent of Code 2022, Day 7
# (c) blu3r4y

from aocd.models import Puzzle
from funcy import print_calls
from parse import parse


class Node:
    def __init__(self, name, size=0, childs=None, parent=None):
        self.name = name
        self.size = size
        self.childs = childs or {}
        self.parent = parent

    def cd(self, path):
        if path == "/":
            raise ValueError("not implemented")
        elif path == "..":
            return self.parent
        else:
            return self.touch(path, size=0)

    def touch(self, name, size=0):
        if name in self.childs:
            return self.childs[name]

        node = Node(name, size, parent=self)
        self.childs[name] = node
        return node

    def isdir(self):
        return self.size == 0

    def isfile(self):
        return self.size > 0

    def dirsize(self):
        if self.isfile():
            return self.size
        return sum(child.dirsize() for child in self.childs.values())

    def get_all_dirs(self):
        if self.isdir():
            yield self
        for child in self.childs.values():
            yield from child.get_all_dirs()

    def __repr__(self) -> str:
        nodetype = "Dir" if self.isdir() else "File"
        return f"{nodetype}({self.name}, size={self.size}, dirsize={self.dirsize()} childs={self.childs})"


@print_calls
def part1(root, max_size=100_000):
    total = 0
    for dir in root.get_all_dirs():
        if dir.dirsize() <= max_size:
            total += dir.dirsize()

    # total size of all directors <= max_size
    return total


@print_calls
def part2(root, disk_size=70_000_000, update_size=30_000_000):
    free_space = disk_size - root.dirsize()
    candidates = []
    for d in root.get_all_dirs():
        if free_space + d.dirsize() >= update_size:
            candidates.append(d.dirsize())

    # smallest size of a directory that we can delete to find the update
    return min(candidates)


def load(data):
    root = Node("/")
    pwd = root

    i, lines = 1, data.split("\n")
    while i < len(lines):
        line = lines[i]

        # perform cd instruction
        if line.startswith("$ cd"):
            path = parse("$ cd {}", line)[0]
            pwd = pwd.cd(path)
            i += 1

        # parse and perform ls output
        if line.startswith("$ ls"):
            i += 1
            while i < len(lines) and not lines[i].startswith("$"):
                line = lines[i]
                if line.startswith("dir"):
                    path = parse("dir {}", line)[0]
                    pwd.cd(path)
                else:
                    size, file = parse("{:d} {}", line).fixed
                    pwd.touch(file, size)
                i += 1

    # print(root)
    return root


if __name__ == "__main__":
    puzzle = Puzzle(year=2022, day=7)

    ans1 = part1(load(puzzle.input_data))
    assert ans1 == 1723892
    # puzzle.answer_a = ans1
    ans2 = part2(load(puzzle.input_data))
    # puzzle.answer_b = ans2
    assert ans2 == 8474158
