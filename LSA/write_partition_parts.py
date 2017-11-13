#!/usr/bin/env python

### THIS MAY OCCUPY ~10-50GB OF /tmp SPACE PER JOB

import glob,os
import sys
import argparse
import gzip
import numpy as np
from collections import defaultdict
from fastq_reader import Fastq_Reader
import HashedReads as Hq

# FUNC
def interface():
    parser = argparse.ArgumentParser()

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

    parser.add_argument('-t',
                        required=True,
                        dest='TMP',
                        type=str,
                        metavar='<tmp_dir>',
                        help='Directory for temporary files.')

    parser.add_argument('-r',
                        required=True,
                        dest='task_rank',
                        type=int,
                        help='Task rank of the current job.')    

    args = parser.parse_args()
    return args

def max_log_lik_ratio(s,bkg,h1_prob=0.8,thresh1=3.84,thresh2=np.inf):
    LLR = [(None,None)]
    read_match_sum = s[-1]
    del s[-1]
    v1 = read_match_sum * h1_prob * (1 - h1_prob)
    m1 = read_match_sum * h1_prob
    for k,sect_sum in s.items():
        if sect_sum > read_match_sum * bkg[k]:
            v2 = read_match_sum * bkg[k] * (1 - bkg[k])
            m2 = read_match_sum * bkg[k]
            llr = np.log(v2**.5/v1**.5) + .5 * ((sect_sum-m2)**2/v2 - (sect_sum-m1)**2/v1)
            LLR.append((llr,k))
    LLR.sort(reverse=True)
    K = []
    if LLR[0][0] > thresh1:
        K.append(LLR[0][1])
    for llr,k in LLR[1:]:
        if llr > thresh2:
            K.append(k)
        else:
            break
    return K

# MAIN
if __name__ == "__main__":
    args = interface()

    input_dir = os.path.abspath(args.IN)
    if not input_dir.endswith('/'):
        input_dir += '/'

    output_dir = os.path.abspath(args.OUT)
    if not output_dir.endswith('/'):
        output_dir += '/'

    tmp_dir = os.path.abspath(args.TMP)
    if not tmp_dir.endswith('/'):
        tmp_dir += '/'

    task_rank = args.task_rank - 1

    hashobject = Fastq_Reader(input_dir, output_dir)
    cp = np.load(hashobject.output_path + 'cluster_probs.npy')
    cluster_probs = dict(enumerate(cp))
    Hashq_Files = glob.glob(os.path.join(hashobject.input_path, '*.hashq.*'))
    Hashq_Files = [fp for fp in Hashq_Files if '.tmp' not in fp]
    Hashq_Files.sort()

    infile = Hashq_Files[task_rank]
    outpart = infile[-6:-3]
    sample_id = infile[infile.rfind('/') + 1:infile.index('.hashq')]
    tmp_dir += 'tmp{0}/'.format(task_rank)
    os.system('mkdir ' + tmp_dir)

    G = [open('{0}{1}.{2}.cols.{3}'.format(tmp_dir, sample_id, outpart, i), 'w') for i in range(0, 2**hashobject.hash_size, 2**hashobject.hash_size / 50)]
    with gzip.open(infile) as f:
        r_id = 0
        for hashed_read in Hq.hash_read_generator(f):
            for b in hashed_read.bins:
                G[int(b * 50 / 2**hashobject.hash_size)].write('{0}\t{1}\n'.format(b, r_id))
            r_id += 1
        R = r_id

    for g in G:
        g.close()
    if R < 50:
        print 'Fewer than 50 reads...doing nothing'
    else:
        ClusterFile = open(hashobject.output_path + 'cluster_cols.npy')
        ValueFile = open(hashobject.output_path + 'cluster_vals.npy')
        G = [open('{0}{1}.{2}.ids.{3}'.format(tmp_dir, sample_id, outpart, i), 'w') for i in range(0, R, R / 50)]
        # If sharing ClusterFile among many jobs is not practical, we may aggregate jobs below by 1/50 ClusterFile fractions across samples (so each job reads 1 fraction)
        for i in range(0, 2**hashobject.hash_size, 2**hashobject.hash_size / 50):
            os.system('sort -nk 1 {0}{1}.{2}.cols.{3} -o {0}{1}.{2}.cols.{3}'.format(tmp_dir, sample_id, outpart, i))
            with open('{0}{1}.{2}.cols.{3}'.format(tmp_dir, sample_id, outpart, i)) as f:
                ColId = np.fromfile(f, dtype=np.int64, sep='\t')
        
            os.system('rm {0}{1}.{2}.cols.{3}'.format(tmp_dir, sample_id, outpart, i))
            C = np.fromfile(ClusterFile, dtype=np.int16, count=5*min(2**hashobject.hash_size / 50, 2**hashobject.hash_size - i))
            V = np.fromfile(ValueFile, dtype=np.float32, count=min(2**hashobject.hash_size / 50, 2**hashobject.hash_size - i))
            c0 = None
            outlines = [[] for _ in G]
            for j in range(0, len(ColId), 2):
                col, id = ColId[j:j + 2]
                if col != c0:
                    ci = col % (2**hashobject.hash_size / 50)
                    c = C[ci * 5:(ci + 1) * 5]
                    c = c[np.nonzero(c)[0]] - 1
                    c0 = col
                if len(c) > 0:
                    v = V[ci]
                    newline = '{0}\t{1}'.format(id,v)
                    for x in c:
                        newline += '\t{0}'.format(x)
                    outlines[id * 50 / R].append(newline + '\n')
            for g, l in zip(G, outlines):
                g.writelines(l)
            del C
            del V
        ClusterFile.close()
        ValueFile.close()
        for g in G:
            g.close()
        for i in range(0, R, R / 50):
            os.system('sort -nk 1 {0}{1}.{2}.ids.{3} -o {0}{1}.{2}.ids.{3}'.format(tmp_dir, sample_id, outpart, i))

        with gzip.open(infile) as f:
            r_id = 0
            G = iter(open('{0}{1}.{2}.ids.{3}'.format(tmp_dir, sample_id, outpart, i)) for i in range(0, R, R / 50))
            g = G.next()
            id_vals = np.fromstring(g.readline(), sep='\t')

            EOF = False
            CF = {}
            reads_written = 0
            unique_reads_written = 0
            for hashed_read in Hq.hash_read_generator(f):
                while id_vals[0] < r_id:
                    id_vals = np.fromstring(g.readline(), sep='\t')
                    # revert to gross old behavior
                    if len(id_vals) == 0:
                        id_vals = [-1]
                    if id_vals[0] == -1:
                        try:
                            g = G.next()
                            id_vals = np.fromstring(g.readline(), sep='\t')
                            # revert to gross old behavior
                            if len(id_vals) == 0:
                                id_vals = [-1]
                        except:
                            EOF = True
                if EOF:
                    break
                D = defaultdict(float)
                while id_vals[0] == r_id:
                    D[-1] += id_vals[1]
                    for clust in id_vals[2:]:
                        D[clust] += id_vals[1]
                    try:
                        id_vals = np.fromstring(g.readline(), sep='\t')
                        # revert to gross old behavior
                        if len(id_vals) == 0:
                            id_vals = [-1]
                    except:
                        break
                #best_clust = max_log_lik_ratio(D, cluster_probs)
                #if best_clust != None:
                best_clusts = max_log_lik_ratio(D, cluster_probs)
                for best_clust in best_clusts:
                    if best_clust not in CF:
                        try:
                            CF[best_clust] = open('{0}{1}/{2}.fastq.{3}'.format(hashobject.output_path, best_clust, sample_id, outpart), 'a')
                        except:
                            os.system('mkdir {0}{1}/'.format(hashobject.output_path, best_clust))
                            CF[best_clust] = open('{0}{1}/{2}.fastq.{3}'.format(hashobject.output_path, best_clust, sample_id, outpart), 'a')
                    CF[best_clust].write(hashed_read.name + '\n')
                    reads_written += 1
                if len(best_clusts) > 0:
                    unique_reads_written += 1
                if len(CF) > 200:
                    for cfv in CF.values():
                        cfv.close()
                    CF = {}
                r_id += 1
        for f in CF.values():
            f.close()
        os.system('rm -rf ' + tmp_dir)
        print('Total reads written: ' + str(reads_written))
        print('Unique reads written: ' + str(unique_reads_written))
        
