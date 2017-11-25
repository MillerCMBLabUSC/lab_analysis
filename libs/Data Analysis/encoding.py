import heapq
import os


class Tree:

    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

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

    def order(self,other):
        if self.


class Huff:

    def __init__(self, path):
        self.path = path
        self.heap = []
        #need some stuff here for decoding

    def split(self, input):
        """ Splits our input into seperate strings by the space delimiter"""
        if input is not None:
            input = input.split()

        return input

    def dict(self, input):
        """Create our frequency dictionary in the form: symbol: frequency; symbol frequency...."""
        frequency = {}
        if input is not None:
            for i in len(input):
                for j in input[i]:
                    if j in frequency:
                        frequency[j] = frequency[j] + 1
                    else:
                        frequency[j] = 1

            return frequency

    def base_heap(self, freq):
        """Defines the base heap (set of bottom nodes) bases on the frequency dictionary. We want to define a particular
        order for our base heap, and thus sort the fre"""
        for i in freq:
            node = Tree(i, freq(i))
            heapq.heappush(self.heap, node)




