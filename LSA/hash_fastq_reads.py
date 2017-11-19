#!/usr/bin/env python

import glob
import os
import sys 
import argparse
import gzip
import io
from fastq_reader import Fastq_Reader
import Fastq as Fq
import HashedReads as Hq

# FUNC
def interface():
    parser = argparse.ArgumentParser(description="Creates jobs.")

    parser.add_argument('-r',
                        required=True,
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
def kmer_bins(b,IDs,outfile):
    current_id = ''
    pair = []
    bins = []
    reads_hashed = 0
    for n in range(len(IDs)):
        read_id = IDs[n]
        if read_id != current_id:
            if len(bins) > 0 and read_id[:-1] != current_id[:-1]:
                for ID in pair:
                    hashed_read = Hq.HashedRead(ID, hashobject.kmer_size, bins)
                    if hashed_read.is_valid():
                        hashed_read.write_to_file(outfile)
                        reads_hashed += 1
                pair = []
                bins = []
            current_id = read_id
            pair.append(IDs[n])
        bins.append(b[n])
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
    reads_file_name = hashobject.input_path + file_prefix + '.fastq' + file_split

    with Fq.open_gz(reads_file_name) as f:
        hashobject.quality_codes = Fq.set_quality_codes(reads_file_name)
        print(reads_file_name)
        with gzip.open(hashobject.output_path + file_prefix + '.hashq' + file_split + '.gz', 'wt') as g:
                IDs = []
                reads_hashed = 0
                print("[HashFastqReads] Starting to hash the reads.")
                IDs, bins = hashobject.generator_to_bins(Fq.fastq_generator(f), rc=do_reverse_compliment)

                print("[HashFastqReads] All k-mers hashed.")
                print("[HashFastqReads] Writing hashed reads to file.")
                for b in range(len(bins)):
                    reads_hashed += kmer_bins(bins[b], IDs, g)

                print("[HashFastqReads] Total reads hashed: " + str(reads_hashed))