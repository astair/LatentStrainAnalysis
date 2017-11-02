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
                        help='The input directory.')

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

    output_dir = os.path.abspath(args.OUT)
    if not output_dir.endswith('/'):
        output_dir += '/'

    k_size = args.KMER
    h_size = args.HASH

    hashobject = Fastq_Reader(input_dir, output_dir, new_hash=(h_size, k_size))
    total_rand_kmers = k_size * h_size * 2
    # hashobject.rand_kmers_for_wheel(total_rand_kmers)
    hashobject.set_wheels(wheels=1)
    # os.remove(input_dir + 'random_kmers.fastq')
    with open(output_dir + 'hashParts.txt','w') as f:
        f.write('{0}\n'.format(2**h_size / 10**6 + 1))
