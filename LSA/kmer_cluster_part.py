#!/usr/bin/env python

import sys
import argparse
import glob, os
import numpy as np
from gensim import models
from streaming_eigenhashes import StreamingEigenhashes

# FUNC
def interface():
    parser = argparse.ArgumentParser()

    parser.add_argument('-i',
                        required=True,
                        dest='IN',
                        type=str,
                        metavar='<input_dir>',
                        help='The directory containing the hashed reads.')

    parser.add_argument('-o',
                        required=True,
                        dest='OUT',
                        type=str,
                        metavar='<output_dir>',
                        help='Cluster vector directory to output the results.')

    parser.add_argument('-r',
                        required=True,
                        dest='task_rank',
                        type=int,
                        help='Task rank of the current job.')    

    parser.add_argument('-t',
                        dest='threshold',
                        default='0.7',
                        type=float,
                        help='Threshold affects the partitioning resolution. Recommendation: 0.5-0.65 for large scale (Tb), 0.6-0.8 for medium scale (100Gb), >0.75 for small scale (10Gb) datasets.')

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
    thresh = args.threshold

    hashobject = StreamingEigenhashes(input_dir,output_dir,get_pool=-1)
    Kmer_Hash_Count_Files = glob.glob(os.path.join(hashobject.input_path,'*.count.hash.conditioned'))

    hashobject.path_dict = {}
    for i in range(len(Kmer_Hash_Count_Files)):
        hashobject.path_dict[i] = Kmer_Hash_Count_Files[i]

    lsi = models.LsiModel.load(hashobject.output_path + 'kmer_lsi.gensim')
    Index = np.load(hashobject.output_path + 'cluster_index.npy')
    i = task_rank * 10**6
    o = (i, min(10**6, 2**hashobject.hash_size-i))
    hashobject.cluster_thresh = thresh
    Ci = hashobject.lsi_cluster_part(o, lsi, Index)
    for ci, c in enumerate(Ci):
        try:
            np.save(hashobject.output_path + str(ci) + '/' + str(task_rank) + '.npy', c)
        except IOError:
            os.system('mkdir ' + hashobject.output_path + str(ci))
            np.save(hashobject.output_path + str(ci) + '/' + str(task_rank) + '.npy', c)