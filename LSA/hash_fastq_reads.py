#!/usr/bin/env python

import glob
import os
import sys 
import argparse
import gzip
from fastq_reader import Fastq_Reader

# FUNC
def interface():
    parser = argparse.ArgumentParser(description="Creates jobs.")

    parser.add_argument('-r',
                        dest='task_rank',
                        type=int,
                        help='Task rank of the current job.')

    parser.add_argument('-i',
                        required=True,
                        dest='IN',
                        type=str,
                        metavar='<input_dir>',
                        help='The directory containing the original reads.')

    parser.add_argument('-o',
                        required=True,
                        dest='OUT',
                        type=str,
                        metavar='<output_dir>',
                        help='The output directory for the hashed reads.')

    parser.add_argument('-z',
                        dest='rev_comp',
                        action='store_false',
                        help='Use this switch to turn off reverse complement.')

    parser.add_argument('-s',
                        dest='sep',
                        default='/',
                        help='This sets the separator for paired files. Default: "/".')

    args = parser.parse_args()
    return args

# PAIRED READ FILES ARE ASSUMED TO BE SORTED
def kmer_bins(b,A,pfx,outfile,type=2):
    if type == 1:
        # use this for readid 1, readid 2 pairs
        def get_id(a):
            return a[:a.index(' ')+2]
    elif type == 2:
        # use this for readid/1, readid/2 pairs
        def get_id(a):
            return a.split()[0]
    else:
        # no known read type treated as singleton
        def get_id(a):
            return a.split()[0]+'*'
    current_id = None
    pair = []
    bins = []
    reads_hashed = 0
    for a in range(len(A)):
        read_id = get_id(A[a])
        print(read_id)
        if read_id != current_id:
            if (len(bins) > 0) and (read_id[:-1] != current_id[:-1]):
                for rp in pair:
                    outfile.write(rp)
                    outfile.write(pfx+','.join([str(x) for x in bins]) + ']\n')
                    reads_hashed += 1
                pair = []
                bins = []
            current_id = read_id
            pair.append(A[a])
        bins.append(b[a])
    return reads_hashed


# MAIN
if __name__ == "__main__":
    args = interface()

    input_dir = os.path.abspath(args.IN)
    if not input_dir.endswith('/'):
        input_dir += '/'

    output_dir = os.path.abspath(args.OUT)
    if not output_dir.endswith('/'):
        output_dir += '/'

    task_rank = args.task_rank - 1
    do_reverse_compliment = args.rev_comp

    FP = glob.glob(os.path.join(input_dir,'*.fastq.*'))
    if len(FP) == 0:
        # single file per-sample
        FP = glob.glob(os.path.join(input_dir,'*.fastq'))

    file_prefix = FP[task_rank]
    file_split = file_prefix[file_prefix.index('.fastq') + 6:]
    file_prefix = file_prefix[file_prefix.rfind('/') + 1:file_prefix.index('.fastq')]

    hashobject = Fastq_Reader(input_dir, output_dir)
    with open(hashobject.input_path + file_prefix + '.fastq' + file_split,'r') as f:
        read_type = 2
        with gzip.open(hashobject.output_path + file_prefix + '.hashq' + file_split + '.gz', 'wb') as g:
            hashobject.hpfx = hashobject.hpfx + str(hashobject.kmer_size)+','
            A = []
            reads_hashed = 0
            while A != None:
                try:
                    A, B = hashobject.generator_to_bins(hashobject.read_generator(f, max_reads=25000, verbose_ids=True), rc=do_reverse_compliment)
                    for b in range(len(B)):
                        reads_hashed += kmer_bins(B[b], A, hashobject.hpfx, g, read_type)
                except Exception as err:
                    pass
                    print(str(err))
            print('total reads hashed:', reads_hashed)