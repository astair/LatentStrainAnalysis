# CLASS 
class Fastq(object):
    """Fastq object with name and sequence
    """

    def __init__(self, name, sequence, name2, qual):
        self.name = name
        self.seq = sequence
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
        valid_id = self.name.startswith('@')
        valid_len = len(self.len) > 1
        valid_qual = len(self.qual) == len(self.seq)
        valid_plus = self.name2 == '+'
        return valid_id and valid_len and valid_qual and valid_plus

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
                yield Fastq(name, seq, name2, qual)


    def open_gz(infile, mode="r"):
        """Takes input and uncompresses gzip if needed
        """

        if infile.endswith(".gz"):
            return gzip.open(infile, mode=mode)
        else:
            return open(infile, mode=mode)