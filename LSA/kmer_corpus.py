#!/usr/bin/env python

import sys
import argparse
import glob, os
import numpy as np
from streaming_eigenhashes import StreamingEigenhashes

# FUNC
def interface():
    parser = argparse.ArgumentParser(description="Writing martix rows to separate files, and computing local (sample) conditioning.")

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
                        metavar='<task_rank>',
                        help='The rank of the currant task.')

    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = interface()

    input_dir = os.path.abspath(args.IN)
    if not input_dir.endswith('/'):
        input_dir += '/'

    output_dir = os.path.abspath(args.OUT)
    if not output_dir.endswith('/'):
        output_dir += '/'

    task_rank = args.task_rank - 1 

    hashobject = StreamingEigenhashes(input_dir,output_dir,get_pool=False)
    Kmer_Hash_Count_Files = glob.glob(os.path.join(hashobject.input_path,'*.count.hash'))
    print(Kmer_Hash_Count_Files)
    #M = np.load(hashobject.input_path+'column_mask.npy')
    M = []
    hashobject.kmer_corpus_to_disk(Kmer_Hash_Count_Files[task_rank],mask=M)