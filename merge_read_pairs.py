#!/usr/bin/env python

import sys,os,glob


if __name__ == "__main__":
	try:
		inputdir = sys.argv[1]
		FP = glob.glob(os.path.join(inputdir,'*.fastq'))
		FP.sort()
		pair1,pair2,sing = FP
		out = 'original_reads/' + inputdir + '.fastq'
		f1 = open(pair1)
		f2 = open(pair2)
		f0 = open(out,'w')
		last = None
		while last != f1.tell():
			last = f1.tell()
			for _ in range(4):
				f0.write(f1.readline())
			for _ in range(4):
				f0.write(f2.readline())
		f1.close()
		f2.close()
		f0.close()
		os.system('cat '+sing+' >> '+out)
		os.system('rm -r '+inputdir)
	except Exception,err:
		print str(err)