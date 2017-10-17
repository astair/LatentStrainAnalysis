#!/usr/bin/env python

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
    """Takes a fastq file infile and returns a fastq object iterator
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

def get_record(infile, position):
    """Takes a fastq file_object and returns a fastq object iterator
    """

    fastq = fastq_parser(infile)
    record = next(fastq)
    for n in range(0, position):
        record = next(fastq)

    return record

def open_gz(infile, mode="r"):
    """Takes input and uncompresses gzip if needed
    """

    if infile.endswith(".gz"):
        return gzip.open(infile, mode=mode)
    else:
        return open(infile, mode=mode)
