#!/usr/bin/env python

import numpy as np

# CLASS 
class HashedRead(object):
    """Hashq object with name, k and bins
    """

    def __init__(self, name, k, bins):
        self.name = name
        self.k = k
        self.bins = bins

    def get_shortname(self, separator):
        if separator:
            self.temp = self.name.split(separator)
            del(self.temp[-1])
            return separator.join(self.temp)
        else:
            return self.name

    def write_to_file(self, handle):
        handle.write(self.name + "\n")
        handle.write(self.bins + "\n")

# FUNC
def hash_read_parser(infile):
    """Parses a HASHQ file and returns a HashedRead object iterator
    """

    with open_gz(infile) as f:
        while True:
            name = str(f.readline().strip())
            if not name:
                break

            info = str(f.readline()).strip().split('[')[1].split(']')[0].split(',')
            k = int(info[0])
            bins = [int(b) for b in info[1:]]
            yield HashedRead(name, k, bins)

def hash_read_generator(f, max_reads=10**15):
    """Reads max_reads from an open HASHQ file and returns a HashedRead object iterator
    """

    for n in range(max_reads):
        name = str(f.readline().strip())
        if not name:
            break

        info = str(f.readline()).strip().split('[')[1].split(']')[0].split(',')
        k = int(info[0])
        bins = np.array([int(b) for b in info[1:]])
        yield HashedRead(name, k, bins)
