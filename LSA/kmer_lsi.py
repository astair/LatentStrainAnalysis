#!/usr/bin/env python

import sys
import argparse
import glob, os
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

    parser.add_argument('-p', '--numproc',
                        dest='numproc',
                        type=int,
                        default='-1',
                        metavar='<numproc>')

    parser.add_argument('-s', '--single',
                        dest='single',
                        action='store_true')

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
    
    num_proc = args.numproc
    singleInstance = args.single
    
    ###
    hashobject = StreamingEigenhashes(input_dir,output_dir,get_pool=num_proc)
    Kmer_Hash_Count_Files = glob.glob(os.path.join(hashobject.input_path,'*.count.hash.conditioned'))
    hashobject.path_dict = {}
    for i in range(len(Kmer_Hash_Count_Files)):
        hashobject.path_dict[i] = Kmer_Hash_Count_Files[i]
    corpus = hashobject.kmer_corpus_from_disk()
    # This is a hack. Should do a better job chosing num_dims
    lsi = hashobject.train_kmer_lsi(corpus, num_dims=len(hashobject.path_dict) * 4 / 5, single=singleInstance)
    lsi.save(hashobject.output_path + 'kmer_lsi.gensim')
    