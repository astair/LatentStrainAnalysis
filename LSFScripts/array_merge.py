#!/usr/bin/env python

import os
import sys
import argparse

# FUNC
def interface():
    parser = argparse.ArgumentParser(description="Creates command line to merge and split paired files.")

    parser.add_argument('-1',
                        required=True,
                        dest='READS_1',
                        nargs='+',
                        type=str,
                        metavar='<reads_1>',
                        help='Comma separated list of R1 reads.')    

    parser.add_argument('-2',
                        required=True,
                        dest='READS_2',
                        nargs='+',
                        type=str,
                        metavar='<reads_2>',
                        help='Comma separated list of R2 reads.')

    parser.add_argument('-s',
                        dest='SINGLETS',
                        nargs='+',
                        type=str,
                        metavar='<singlets>',
                        help='Comma separated list of unpaired reads.')

    parser.add_argument('-r',
                        dest='task_rank',
                        type=int,
                        help='Task rank of the current job.')

    parser.add_argument('-o', '--output-dir',
                        required=True,
                        dest='out',
                        type=str,
                        metavar='<output-directory>',
                        help='Output directory for splitting the reads.')

    args = parser.parse_args()
    return args



if __name__ == "__main__":
    args = interface()

    reads_1 = sorted(args.READS_1)
    reads_2 = sorted(args.READS_2)
    reads_single = sorted(args.SINGLETS)

    task_rank = args.task_rank

    output_dir = args.out
    if not output_dir.endswith('/'):
        output_dir += '/'

    try:
        curr_reads_1 = reads_1[task_rank]
    except IndexError:
        curr_reads_1 = None    

    try:
        curr_reads_2 = reads_2[task_rank]
    except IndexError:
        curr_reads_2 = None    

    try:
        curr_single = reads_single[task_rank]
    except IndexError:
        curr_single = None

    # This I can do better, but this should work for now:
    out = output_dir + curr_reads_1.split('/')[-1].split('.')[0]
    os.system('merge_and_split_pair_files.py -1 {0} -2 {1} -s {2} -o {3}'.format(curr_reads_1, curr_reads_2, curr_single, out))

