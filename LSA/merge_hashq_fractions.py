#!/usr/bin/env python

import sys
import argparse
import glob
import os
import numpy as np
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

    FP = glob.glob(os.path.join(input_dir,'*.hashq.*'))
    FP = [fp[fp.rfind('/')+1:] for fp in FP]
    FP = list(set([fp[:fp.index('.')] for fp in FP]))
    file_prefix = FP[task_rank]
    hashobject = Fastq_Reader(input_dir, output_dir)
    H = hashobject.merge_count_fractions(file_prefix)
    H = np.array(H, dtype=np.uint16)
    nz = np.nonzero(H)[0]
    np.save(hashobject.output_path + file_prefix + '.nonzero.npy', nz)
    print('sample {0} has {1} nonzero elements and {2} total observed kmers'.format(file_prefix, len(nz), H.sum()))