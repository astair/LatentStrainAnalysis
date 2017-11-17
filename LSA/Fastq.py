#!/usr/bin/env python

import gzip

# CLASS 
class FastqRecord(object):
    """Fastq object with name and sequence
    """

    def __init__(self, name, sequence, name2, qual):
        self.name = name
        self.seq = sequence.upper()
        self.name2 = name2
        self.qual = qual

    def get_shortname(self, separator):
        if separator:
            self.temp = self.name.split(separator)
            del(self.temp[-1])
            return separator.join(self.temp)
        else:
            return self.name

    def write_to_file(self, handle):
        handle.write(self.name + "\n")
        handle.write(self.seq + "\n")
        handle.write(self.name2 + "\n")
        handle.write(self.qual + "\n")

    def is_valid(self):
        val_id = self.name.startswith('@')
        val_seq = len(set(self.seq)) <= 5
        val_len = len(self.seq) > 1
        val_qual = len(self.qual) == len(self.seq)
        val_plus = self.name2 == '+'
        return val_id and val_len and val_qual and val_plus


# FUNC
def fastq_parser(infile):
    """Takes a FASTQ file infile and returns a FastqRecord object iterator
    """

    with open_gz(infile) as f:
        while True:
            name = f.readline().strip()
            if not name:
                break

            seq = f.readline().strip()
            name2 = f.readline().strip()
            qual = f.readline().strip()
            yield FastqRecord(name, seq, name2, qual)

def fastq_generator(f, max_reads=10**15):
    """Reads max_reads from an open FASTQ file and returns a FastqRecord object iterator
    """

    n = 0
    while n <= max_reads:
        name = f.readline().strip()
        if not name:
            break

        seq = f.readline().strip()
        name2 = f.readline().strip()
        qual = f.readline().strip()
        n += 1
        yield FastqRecord(name, seq, name2, qual)

def get_record(infile, position):
    """Takes a fastq file_object and returns a FastqRecord object
    """

    fastq = fastq_parser(infile)
    record = next(fastq)
    for n in range(0, position):
        record = next(fastq)

    return record

def open_gz(infile, mode="rt"):
    """Takes input and uncompresses gzip if needed
    """

    if infile.endswith(".gz") or ".gz." in infile:
        return gzip.open(infile, mode=mode)
    else:
        return open(infile, mode=mode)

def set_quality_codes(infile):
    """Guesses the format of the quality codes and returns a dict for convarsion
    """

    fastq = fastq_parser(infile)
    sampled_reads = 0
    o33 = 0
    o64 = 0
    for record in fastq:
        while sampled_reads < 1000:
            for c in record.qual:
                oc = ord(c)
                if oc < 74:
                    o33 += 1
                else:
                    o64 += 1
            sampled_reads += 1
    if 3*o33 > o64:
        quality_codes = dict([(chr(x),x-33) for x in range(33,33+94)])
    else:
        quality_codes = dict([(chr(x),x-64) for x in range(64-5,64+63)])
    return quality_codes
