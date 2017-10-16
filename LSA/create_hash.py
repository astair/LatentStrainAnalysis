#!/usr/bin/env python

import sys
import argparse 
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
                        help='The inoput directory.')

    parser.add_argument('-o',
                        required=True,
                        dest='OUT',
                        type=str,
                        metavar='<output_dir>',
                        help='The output directory.')

    parser.add_argument('-k',
                        required=True,
                        dest='KMER',
                        type=int,
                        metavar='<kmersize>',
                        help='Kmer size.')

    parser.add_argument('-s',
                        required=True,
                        dest='HASH',
                        type=int,
                        metavar='<hashsize>',
                        help='Hash size.')

    

    args = parser.parse_args()
    return args


# MAIN
if __name__ == "__main__":
	args = interface()

    input_dir = os.path.abspath(args.IN)
    if not input_dir.endswith('/'):
        input_dir += '/'

    output_dir = os.path.abspath(args.IN)
    if not output_dir.endswith('/'):
        output_dir += '/'

	hashobject = Fastq_Reader(inputdir,outputdir,new_hash=(h_size,k_size))
	total_rand_kmers = k_size * h_size * 2
	hashobject.rand_kmers_for_wheel(total_rand_kmers)
	hashobject.set_wheels(wheels=1)
	os.system('rm %s/random_kmers.fastq' % inputdir)
	with open(outputdir + 'hashParts.txt','w') as f:
		f.write('%d\n' % (2**h_size / 10**6 + 1))
