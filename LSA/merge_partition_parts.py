#!/usr/bin/env python

import sys
import argparse
import glob,os

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

    parser.add_argument('-t',
                        dest='threshold',
                        type=float,
                        help='Threshold.')

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

	task_rank = str(task_rank)+'/'
	os.system('mkdir '+output_dir+task_rank)
	FP = glob.glob(os.path.join(input_dir+task_rank,'*.fastq.*'))
	FPl = list(set([fp[fp.rfind('/')+1:fp.index('.fastq')] for fp in FP]))
	for group in FPl:
		gp = [fp for fp in FP if input_dir+task_rank+group+'.fastq' == fp[:fp.rfind('.')]]
		#gp = [fp for fp in gp if '.empty' not in fp]
		if len(gp) > 0:
			os.system('cat '+' '.join(gp)+' > '+output_dir+task_rank+group+'.fastq')
			#os.system('touch %s.empty' % (gp[0]))
			os.system('rm '+' '.join(gp))