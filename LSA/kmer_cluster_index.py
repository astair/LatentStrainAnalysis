#!/usr/bin/env python

import sys
import argparse
import glob, os
import numpy as np
from gensim import models
from streaming_eigenhashes import StreamingEigenhashes

# FUNC
def interface():
    parser = argparse.ArgumentParser(description="Creates jobs.")

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

    task_rank = args.task_rank
    thresh = args.threshold

	hashobject = StreamingEigenhashes(inputdir,outputdir,get_pool=-1)
	Kmer_Hash_Count_Files = glob.glob(os.path.join(hashobject.input_path,'*.count.hash.conditioned'))
	hashobject.path_dict = {}
	for i in range(len(Kmer_Hash_Count_Files)):
		hashobject.path_dict[i] = Kmer_Hash_Count_Files[i]
	lsi = models.LsiModel.load(hashobject.output_path+'kmer_lsi.gensim')
	hashobject.cluster_thresh = thresh
	Index = hashobject.lsi_cluster_index(lsi)
	np.save(hashobject.output_path+'cluster_index.npy',Index)
	print 'cluster index has shape:',Index.shape
	f = open(hashobject.output_path+'numClusters.txt','w')
	f.write('%d\n' % Index.shape[0])
	f.close()