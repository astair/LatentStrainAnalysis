#!/usr/bin/env python

import sys
import getopt
import os

# FUNC
def interface():
    parser = argparse.ArgumentParser(description="Setup the directories necessary for the pipeline in <output-dir>")

    parser.add_argument('-i', '--input-dir',
    					dest='input',
                        type=str,
                        metavar='<input-dir>',
                        help='Directory with reads to process.')

    parser.add_argument('-n',
    					dest='n',
                        type=int,
                        metavar='<sample-num>',
                        help='Number of samples.')

    parser.add_argument('-o', '--output-dir',
                        dest='out',
                        type=str,
                        metavar='<output-directory>',
                        help='Output directory for the pipeline.')

    args = parser.parse_args()
    return args


SplitInput_string = """#!/bin/bash
#BSUB -J SplitInput[1-{0}]
#BSUB -o Logs/SplitInput-Out-%I.out
#BSUB -e Logs/SplitInput-Err-%I.err
#BSUB -q week
#BSUB -W 23:58
echo Date: `date`
t1=`date +%s`
sleep ${{LSB_JOBINDEX}}
array_merge.py -r ${{LSB_JOBINDEX}} -i {1} -o original_reads/
[ $? -eq 0 ] || echo 'JOB FAILURE: $?'
echo Date: `date`
t2=`date +%s`
tdiff=`echo 'scale=3;('$t2'-'$t1')/3600' | bc`
echo 'Total time:  '$tdiff' hours'
"""

# MAIN
if __name__ == "__main__":
	args = interface()
	input_dir = args.input
	output_dir = args.out
	sample_num = args.n

	dir_names = ['Logs','original_reads','hashed_reads','cluster_vectors','read_partitions']

	for d in dir_names:
		os.system('mkdir {0}'.format(d))
	f = open('{0}/SplitInput_ArrayJob.q'.format(output_dir),'w')
	f.write(SplitInput_string.format(sample_num, input_dir))
	f.close()
