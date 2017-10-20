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

    def hash_read_generator(self,file_object,max_reads=10**15,newline='\n'):
        line = file_object.readline().strip()
        lastlinechar = ''
        read_strings = []
        r = 0
        while (line != '') and (r < max_reads):
            # read_id (always) and quality (sometimes) begin with '@', but quality preceded by '+' 
            if (line[0] == '@') and (lastlinechar != '+'):
                if len(read_strings) == 5:
                    try:
                        I = newline.join(read_strings[:-1])
                        B = np.fromstring(read_strings[-1][10:-2],dtype=np.uint64,sep=',')
                        yield (I,B[0],B[1:])
                    except Exception as err:
                        print(str(err))
                    r += 1
                read_strings = []
            read_strings.append(line)
            lastlinechar = line[0]
            line = file_object.readline().strip()

    def rand_kmers_for_wheel(self,total_kmers):
        read_files = glob.glob(os.path.join(self.input_path, '*.fastq.*'))
        if len(read_files) > 100:
            import random
            read_files = random.sample(read_files, 100)
        elif len(read_files) == 0:
            # single file per sample
            read_files = glob.glob(os.path.join(self.input_path, '*.fastq'))

        kmers_per_file = max(total_kmers / len(read_files), 5)

        with open(self.input_path + 'random_kmers.fastq', 'w') as g:
            kmer_count = 0
            for file in read_files:
                while kmer_count < total_kmers:
                    written_kmers = 0
                    fails = 0
                    while written_kmers < kmers_per_file:
                        try:
                            g.write(self.rand_kmer(file))
                            written_kmers += 1
                        except Exception as err:
                            fails += 1
                            # print(str(err))
                            if fails > 100:
                                print('\nGeneration of kmers failed too many times\n') 
                                raise
                    kmer_count += written_kmers

    def rand_kmer(self,f,max_seek=10**8):
        too_short = 0
        max_sampling = 100000
        while True:

            # Try retrieving random record, except max_seek exceedes file
            try:
                rand_i = randint(0, max_seek)
                record = Fq.get_record(f, rand_i)
                if record.is_valid() and len(record.seq) > self.kmer_size:
                    break

                # Handle too short or invalid sequences
                if len(record.seq) < self.kmer_size:
                    too_short += 1
                    if too_short > max_sampling:
                        raise Exception('UUUPS, something went wrong while generating random kmers. All of the {1} reads that were sampled were shorter than the set kmer size ({0})'.format(self.kmer_size, max_sampling))
                if not record.is_valid():
                    print(invalid_message.format(f, record.name, rand_i))

            # Narrow it down and raise error if we are down to 0
            except:
                max_seek /= 10
                if max_seek == 0:
                    print('UUUPS, something went wrong while generating random kmers. Your read file might be too short or in the wrong format.')
                    raise 
        rand_pos = min(20, randint(0, len(record.seq) - self.kmer_size))
        return '\n'.join([record.name, record.seq[rand_pos:rand_pos + self.kmer_size], record.name2, record.qual[rand_pos:rand_pos + self.kmer_size] + '\n']) 
