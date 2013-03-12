#!/usr/bin/env python

import sys,getopt
from fastq_reader import Fastq_Reader

help_message = "usage example: python create_hash.py -i /project/home/original_reads/ -o /project/home/hashed_reads/ -k kmer_size -s hash_size"
if __name__ == "__main__":
	try:
		opts, args = getopt.getopt(sys.argv[1:],'hi:o:k:s:',["inputdir=","outputdir=","kmersize=","hashsize="])
	except:
		print help_message
		sys.exit(2)
	for opt, arg in opts:
		if opt in ('-h','--help'):
			print help_message
			sys.exit()
		elif opt in ('-i','--inputdir'):
			inputdir = arg
			if inputdir[-1] != '/':
				inputdir += '/'
		elif opt in ('-o','--outputdir'):
			outputdir = arg
			if outputdir[-1] != '/':
				outputdir += '/'
		elif opt in ('-k','--kmersize'):
			k_size = int(arg)
		elif opt in ('-s','--hashsize'):
			h_size = int(arg)
	hashobject = Fastq_Reader(inputdir,outputdir,new_hash=(h_size,k_size))
	total_rand_kmers = k_size*h_size*2
	hashobject.rand_kmers_for_wheel(total_rand_kmers)
	hashobject.set_wheels(wheels=1)