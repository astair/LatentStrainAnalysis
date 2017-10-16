#!/usr/bin/env python

import sys
import os
import argparse


# FUNC
def interface():
    parser = argparse.ArgumentParser(description="Merges paired files and splits singeltons.")

    parser.add_argument('-1',
                        required=True,
                        dest='READS_1',
                        type=str,
                        metavar='<reads_1>',
                        help='File with R1 reads.')    

    parser.add_argument('-2',
                        required=True,
                        dest='READS_2',
                        type=str,
                        metavar='<reads_2>',
                        help='File with R2 reads.')
    
    parser.add_argument('-s',
                        dest='SINGLETS',
                        type=str,
                        metavar='<singlets>',
                        help='File with unpaired reads.')

    parser.add_argument('-o', '--output-prefix',
                        required=True,
                        dest='out',
                        type=str,
                        metavar='<output-prefix>',
                        help='Prefix for output files.')

    args = parser.parse_args()
    return args


def merge_pairs(f1, f2, f0):
    reads_written = 0
    for i in range(0, 2 * 10**6, 10**5):
        r1 = [f1.readline() for _ in range(10**5)]
        r2 = [f2.readline() for _ in range(10**5)]
        try:
            while (r1[0].strip().split()[0][:-1] != r2[0].strip().split()[0][:-1]) and (r1[0][0] != '@'):
                r1 = r1[1:]
                r2 = r2[1:]
        except:
            r1 = ['']
            r2 = ['']
            pass
        for j in range(0, len(r1), 4):
            f0.writelines(r1[j:j + 4])
            f0.writelines(r2[j:j + 4])
            reads_written += 2
    return len(r1[0]), reads_written


def split_singletons(sing_path, out_prefix):
    ss = 0
    i = 0
    reads_written = 0
    f1 = open(sing_path)

    for line in f1:
        if i % 4000000 == 0:
            f0 = open(out_prefix + '.singleton.fastq' + split_suffix[ss], 'w')
            ss += 1
        f0.write(line)
        reads_written += .25
        i += 1
    return reads_written


# MAIN
if __name__ == "__main__":
    args = interface()

    reads_1 = args.READS_1
    reads_2 = args.READS_2
    reads_single = args.SINGLETS
    out = args.out

    split_suffix = ['.00' + str(_) for _ in range(10)]
    split_suffix += ['.0' + str(_) for _ in range(10,99)]
    split_suffix += ['.' + str(_) for _ in range(100,999)]

    mates_written = 0
    singletons_written = 0

    if reads_1 != 'None' and reads_2 != 'None':
        f1 = open(reads_1)
        f2 = open(reads_2)
        r1len = 1
        ss = 0
        while r1len > 0:
            f0 = open(out + '.interleaved.fastq' + split_suffix[ss],'w')
            r1len, rw = merge_pairs(f1, f2, f0)
            ss += 1
            mates_written += rw
            f0.close()

    if reads_single != 'None':
        rw = split_singletons(reads_single, out)
        singletons_written += rw

    print('mates written: {0}, singletons written: {1}, total reads written: {2}'.format(mates_written, singletons_written, mates_written + singletons_written))

    os.system('touch ' + out + '.fastq')