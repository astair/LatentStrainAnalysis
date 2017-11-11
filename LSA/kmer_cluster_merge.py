#!/usr/bin/env python

import sys
import argparse
import glob, os
import numpy as np

# FUNC
def interface():
    parser = argparse.ArgumentParser()

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

    FP = glob.glob(os.path.join(input_dir + str(task_rank), '*.npy'))
    if len(FP) > 0:
        C = np.empty((10**9, ), dtype=np.uint64)
        ci = 0
        for fp in FP:
            c = np.load(fp)
            C[ci:ci + c.shape[0]] = c
            ci += c.shape[0]
        np.save(output_dir + str(task_rank) + '.cluster.npy', C[:ci])
        os.system('rm -r {0}{1}/'.format(output_dir, task_rank))
    else:
        print('NO FILES: ' + str(task_rank))