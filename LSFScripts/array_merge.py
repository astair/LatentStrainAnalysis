#!/usr/bin/env python

import glob
import os
import sys
import argparse

# FUNC
def interface():
    parser = argparse.ArgumentParser(description="Sets up the directories necessary for the pipeline in <output-dir> and creates the 'SplitInput_ArrayJob.q' script from the input veriables.")

    parser.add_argument('-i', '--input-dir',
    					required=True,
    					dest='input',
                        type=str,
                        metavar='<input-dir>',
                        help='Directory with reads to process.')

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



if __name__ == "__main__":
	args = interface()

	input_dir = args.input
	if not input_dir.endswith('/'):
		input_dir += '/'

	output_dir = args.out
	if not output_dir.endswith('/'):
		output_dir += '/'


		elif opt in ('-r','--filerank'):
			fr = int(arg) - 1

	FP = glob.glob(os.path.join(inputdir,'*.fastq.1'))
	# FP is list of filenames
	FP.sort()
	fp = FP[fr]
	p1 = fp
	p2 = fp[:-1] + '2'
	s = fp[:fp.index('.fastq')] + '.single.fastq.1'
	o = outputdir + fp[fp.rfind('/')+1:fp.index('.fastq')]
	os.system('python LSFScripts/merge_and_split_pair_files.py -1 %s -2 %s -s %s -o %s' % (p1,p2,s,o))
	os.system('python LSFScripts/merge_and_split_pair_files.py -s %s -o %s' % (s[:-1] + '2',o))
