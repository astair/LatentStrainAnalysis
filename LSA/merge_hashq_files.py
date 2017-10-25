#!/usr/bin/env python

import sys
import argparse
import glob
import os
from fastq_reader import Fastq_Reader

# FUNC
def interface():
    parser = argparse.ArgumentParser(description="Creates the hash function.")

    parser.add_argument('-i',
                        required=True,
                        dest='IN',
                        type=str,
                        metavar='<input_dir>',
                        help='The input directory.')

    parser.add_argument('-o',
                        required=True,
                        dest='OUT',
                        type=str,
                        metavar='<output_dir>',
                        help='The output directory.')

    parser.add_argument('-r',
                        required=True,
                        dest='task_rank',
                        type=int,
                        help='Task rank of the current job.')

    args = parser.parse_args()
    return args

def unique(array):
    seen = set()
    seen_add = seen.add
    return [x for x in array if not (x in seen or seen_add(x))]


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

    FP = glob.glob(os.path.join(input_dir, '*.hashq.*'))
    FP = [fp[fp.rfind('/') + 1:] for fp in FP]
    FP = list(unique([fp[:fp.index('.')] for fp in FP]))
    file_prefix = FP[task_rank % len(FP)]

    print('Merging sample ' + file_prefix)

    # SUPER DUMB to hardcode the fraction size
    file_fraction = int(task_rank / len(FP))
    hashobject = Fastq_Reader(input_dir, output_dir)
    H = hashobject.hash_counts_from_hashq(file_prefix, multi_files_fraction=file_fraction)