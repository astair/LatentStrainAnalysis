#!/usr/bin/env python

import sys
import argparse
import glob, os
import numpy as np
from streaming_eigenhashes import StreamingEigenhashes

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

	hashobject = StreamingEigenhashes(input_dir,output_dir,get_pool=-1)
	FP = glob.glob(os.path.join(hashobject.output_path,'*.cluster.npy'))
	FP = [(int(fp[fp.rfind('/')+1:fp.index('.cluster')]),fp) for fp in FP]
	I = np.load(hashobject.output_path+'cluster_index.npy')
	I = I.shape[0]
	cluster_sizes = np.zeros(I,dtype=np.uint64)
	GW = np.load(hashobject.output_path+'global_weights.npy')
	global_weight_sum = GW.sum(dtype=np.float64)
	CP = np.zeros(I)
	X = np.zeros((2**hashobject.hash_size,5),dtype=np.int16)
	Ix = np.zeros(2**hashobject.hash_size,dtype=np.int8)
	for i,fp in FP:
		c = np.load(fp)
		CP[i] = GW[c].sum(dtype=np.float64)/global_weight_sum
		cluster_sizes[i] = c.shape[0]
		X[c,Ix[c]] = i+1
		Ix[c] += 1
	Y = np.memmap(hashobject.output_path+'cluster_cols.npy',dtype=np.int16,mode='w+',shape=(2**hashobject.hash_size,5))
	Y[:] = X
	del Y
	del X
	np.save(hashobject.output_path+'cluster_probs.npy',CP)
	np.save(hashobject.output_path+'kmer_cluster_sizes.npy',cluster_sizes)
	Y = np.memmap(hashobject.output_path+'cluster_vals.npy',dtype=np.float32,mode='w+',shape=GW.shape)
	Y[:] = GW
	del Y
	del GW