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
        handle.write(str(self.k) + "\n")
        handle.write(','.join([str(b) for b in self.bins])  + "\n")

    def is_valid(self):
        try:
            val_name = self.name.startswith('@')
            val_k = int(self.k) > 0
            val_bins = len(list(self.bins)) > 0
            return val_name and val_k and val_bins
        except:
            return False

# FUNC
def hash_read_parser(infile):
    """Parses a HASHQ file and returns a HashedRead object iterator
    """

    with open_gz(infile) as f:
        while True:
            name = str(f.readline().strip())
            if not name:
                break

            info = str(line).strip().split('[')[1].split(']')[0].split(',')
            k = int(info[0])
            bins = [int(b) for b in info[1:]]
            yield HashedRead(name, k, bins)

def hash_read_generator(f, max_reads=10**10):
    """Reads max_reads from an open HASHQ file and returns a HashedRead object iterator
    """

    n = 0
    while n <= max_reads:
        name = str(f.readline().strip())
        if not name:
            break

        line = f.readline().strip()
        k = int(line)
        line = str(f.readline().strip())
        bins = np.fromstring(line, dtype=np.uint64, sep=',')
        n += 1

        yield HashedRead(name, k, bins)
