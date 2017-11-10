#!/usr/bin/env python

import sys
import argparse
import glob, os
from gensim import corpora
import numpy as np
from streaming_eigenhashes import StreamingEigenhashes

# FUNC
def interface():
    parser = argparse.ArgumentParser(description="Global k-mer conditioning for dreation of abundance matrix.")

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


if __name__ == "__main__":
    args = interface()

    input_dir = os.path.abspath(args.IN)
    if not input_dir.endswith('/'):
        input_dir += '/'

    output_dir = os.path.abspath(args.OUT)
    if not output_dir.endswith('/'):
        output_dir += '/'

    hashobject = StreamingEigenhashes(input_dir,output_dir,get_pool=False)
    Kmer_Hash_Count_Files = glob.glob(os.path.join(hashobject.input_path, '*.nonzero.npy'))
    corpus_generator = hashobject.corpus_idf_from_hash_paths(Kmer_Hash_Count_Files)
    hashobject.train_tfidf(corpus_generator)
    np.save(hashobject.output_path + 'global_weights.npy', hashobject.global_weights)