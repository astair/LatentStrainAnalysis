#!/usr/bin/env python

import sys
import argparse
import os

# FUNC
def interface():
    parser = argparse.ArgumentParser(description="Sets up the directories necessary for the pipeline in <output-dir> and creates the 'SplitInput_ArrayJob.q' script from the input veriables.")

    parser.add_argument('-1',
                        dest='READS_1',
                        nargs='+',
                        type=str,
                        metavar='<reads_1>',
                        help='Comma separated list of R1 reads.')    

    parser.add_argument('-2',
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

    parser.add_argument('-n',
                        required=True,                        
                        dest='n',
                        type=int,
                        metavar='<sample-num>',
                        help='Number of samples.')

    parser.add_argument('-o', '--output-dir',
                        required=True,
                        dest='OUT',
                        type=str,
                        metavar='<output-directory>',
                        help='Output directory for the pipeline.')

    args = parser.parse_args()
    return args


SplitInput_string = """#!/bin/bash
#SBATCH -J SplitInput[1-{0}]
#SBATCH --array=1-{0}
#SBATCH -p 1week
#SBATCH -o {1}Logs/SplitInput-Out%I.out
#SBATCH -e {1}Logs/SplitInput-Err%I.err
echo Date: `date`
t1=`date +%s`
array_merge.py -r ${{SLURM_ARRAY_TASK_ID}} -1 {2} -2 {3} -s {4} -o {1}original_reads/
echo Date: `date`
t2=`date +%s`
tdiff=`echo 'scale=3;('$t2'-'$t1')/3600' | bc`
echo 'Total time:  '$tdiff' hours'
"""


# MAIN
if __name__ == "__main__":
    args = interface()
    reads_1 = args.READS_1 
    reads_2 = args.READS_2 
    reads_2 = args.READS_2 
    reads_single = args.SINGLETS 

    if reads_1:
        reads_1 = " ".join(reads_1)
    if reads_2:
        reads_2 = " ".join(reads_2)
    if reads_single:
        reads_single = " ".join(reads_single)

    output_dir = os.path.abspath(args.OUT)
    if not output_dir.endswith('/'):
        output_dir += '/'

    sample_num = args.n

    dir_names = ['Logs','original_reads','hashed_reads','cluster_vectors','read_partitions', 'jobs']

    for d in dir_names:
        if not os.path.exists(output_dir + d):
            os.system('mkdir ' + output_dir + d)

    f = open(output_dir + 'jobs/SplitInput_ArrayJob.q', 'w')
    f.write(SplitInput_string.format(sample_num, output_dir, reads_1, reads_2, reads_single))
    f.close()
