#!/usr/bin/env python

import sys
import argparse
import os

# FUNC
def interface():
	parser = argparse.ArgumentParser(description="Sets up the directories necessary for the pipeline in <output-dir> and creates the 'SplitInput_ArrayJob.q' script from the input veriables.")

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

	parser.add_argument('-n',
						dest='n',
						default='?',
						type=int,
						metavar='<sample-num>',
						help='Number of samples.')

	parser.add_argument('-o', '--output-dir',
						required=True,
						dest='out',
						type=str,
						metavar='<output-directory>',
						help='Output directory for the pipeline.')

	args = parser.parse_args()
	return args


SplitInput_string = """#!/bin/bash
#SBATCH -J SplitInput[1-{0}]
#SBATCH -o {1}Logs/SplitInput-Out.out
#SBATCH -e {1}Logs/SplitInput-Err.err

echo Date: `date`
t1=`date +%s`

array_merge.py -r ${{LSB_JOBINDEX}} -1 {2} -2 {3} -s {4} -o original_reads/

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
	reads_single = args.SINGLETS

	output_dir = args.out
	if not output_dir.endswith('/'):
		output_dir += '/'

	sample_num = args.n

	dir_names = ['Logs','original_reads','hashed_reads','cluster_vectors','read_partitions', 'scripts']

	for d in dir_names:
		os.system('mkdir {0}{1}'.format(output_dir, d))

	f = open('{0}scripts/SplitInput_ArrayJob.q'.format(output_dir),'w')
	f.write(SplitInput_string.format(sample_num, output_dir, reads_1, reads_2, reads_single))
	f.close()
