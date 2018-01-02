#!/usr/bin/env python3
import heapq
import os


class Tree:

    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    """Apparently Python 3 no longer supports __cmp__..."""
    def __add__(self, other):
        if isinstance(other, Tree):
            return Tree(self.freq + other.freq, None, self, other)
        else:
            return NotImplemented

    def __lt__(self, other):
        instance = isinstance(self, Tree)
        if instance:
            return self.freq < other.freq
        else:
            return NotImplemented

    def __le__(self, other):
        instance = isinstance(self, Tree)
        if instance:
            return self.freq <= other.freq
        else:
            return NotImplemented

    def __gt__(self, other):
        instance = isinstance(self, Tree)
        if instance:
            return self.freq > other.freq
        else:
            return NotImplemented

    def __ge__(self, other):
        instance = isinstance(self, Tree)
        if instance:
            return self.freq >= other.freq
        else:
            return NotImplemented



class Huff:

    def __init__(self, path):
        self.path = path
        self.heap = []
        self.codes = {}


    def dict(self, input):
        """Create our frequency dictionary in the form: symbol: frequency; symbol frequency...."""
        frequency = {}

        if input is not None:
            for i in range(len(input)):
                for j in input:
                    if j in frequency:
                        frequency[j] = frequency[j] + 1
                    else:
                        frequency[j] = 1

            return frequency


    def pqueue(self, freq):
        for key in freq:
            self.heap.append(Tree(key, freq[key]))

        heapq.heapify(self.heap)

        while len(self.heap) > 1:
            left = heapq.heappop(self.heap)
            right = heapq.heappop(self.heap)
            node = Tree(None, right.freq + left.freq)
            node.left = left
            node.right = right

            heapq.heappush(self.heap, node)

    def pre_encode(self, s, root):

        if root.char:
            if not s:
                self.codes[root.char] = "0"
            else:
                self.codes[root.char] = s

        else:

            self.pre_encode(s + "0", root.left)
            self.pre_encode(s + "1", root.right)

    def encode(self):
        root = heapq.heappop(self.heap)
        s = ""
        self.pre_encode(s, root)

    def compress(self):

        inp = self.path
        frequency = self.dict(inp)
        self.pqueue(frequency)
        self.encode()

        return self.codes, "".join([self.codes[a] for a in inp])









