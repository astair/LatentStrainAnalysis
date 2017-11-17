#!/usr/bin/env python

from random import randint
import glob,os
import numpy as np
from LSA import LSA
from hyper_sequences import Hyper_Sequences
from hash_counting import Hash_Counting
from cluster_analysis import Cluster_Analysis
import Fastq as Fq

invalid_message = ''''The following read record is not valid:
    File: {0}
    ID: {1}
    Position: {2}'''

class Fastq_Reader(Cluster_Analysis,Hash_Counting,Hyper_Sequences,LSA):

    def __init__(self,indir,outdir,hash_size=999,new_hash=(None,None)):
        super(Fastq_Reader,self).__init__(indir,outdir)
        if new_hash == (None,None):
            try:
                self.get_wheels(spoke_limit=hash_size, wheel_limit=1)
                self.hash_size = self.Wheels[-1]['s'] + 1
                self.kmer_size = len(self.Wheels[0]['p'])
            except:
                raise
                self.Wheels = None
                self.hash_size = None
                self.kmer_size = None
            self.newline_proxy = 'NEWLINE'
        else:
            self.hash_size = new_hash[0]
            self.kmer_size = new_hash[1]

    def rand_kmers_for_wheel(self,total_kmers,max_reads=10**6):
        read_files = glob.glob(os.path.join(self.input_path, '*.fastq.*'))
        if len(read_files) > 100:
            import random
            read_files = random.sample(read_files, 100)
        elif len(read_files) == 0:
            # single file per sample
            read_files = glob.glob(os.path.join(self.input_path, '*.fastq'))

        kmers_per_file = max(total_kmers / len(read_files), 5)

        print("Creating {0} k-mers per file for {1} files.". format(kmers_per_file, len(read_files)))

        with open(self.input_path + 'random_kmers.fastq', 'w') as g:
            kmer_count = 0
            for file in read_files:
                written_kmers = 0
                rand_arr = np.array([random.randint(0, max_reads) for x in range(kmers_per_file)])
                rand_arr.sort()
                fastq = Fq.fastq_parser(file)
                count = 0

                for r in rand_arr:
                    for record in fastq:
                        if count == r:
                            if record.is_valid() and len(record.seq) > self.kmer_size:
                                g.write(self.rand_kmer(record))
                                written_kmers += 1
                                break
                        count += 1

                kmer_count += written_kmers
                if kmer_count > total_kmers:
                    break


    def rand_kmer(self,fastq_record):
        rand_pos = min(20, randint(0, len(fastq_record.seq) - self.kmer_size))
        return '\n'.join([fastq_record.name, fastq_record.seq[rand_pos:rand_pos + self.kmer_size], fastq_record.name2, fastq_record.qual[rand_pos:rand_pos + self.kmer_size]]) + '\n'
