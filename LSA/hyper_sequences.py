import numpy as np
import pickle
from operator import itemgetter
from LSA import LSA
import Fastq as Fq


class Hyper_Sequences(LSA):

	def __init__(self,inputpath,outputpath):
		super(Hyper_Sequences,self).__init__(inputpath,outputpath)

	def generator_to_bins(self,sequence_generator,rc=True):
		IDs = []
		hyper_kmers = []
		for ID, coords in self.generator_to_coords(sequence_generator):
			for i in range(len(coords) - self.kmer_size + 1):
				IDs.append(ID)
				hyper_kmers.append(coords[i:i + self.kmer_size])
		return self.coords_to_bins(IDs, hyper_kmers, reverse_compliments=rc)

	def generator_to_coords(self,sequence_generator):
		for record in sequence_generator:
			coords = self.letters_to_coords(record)
			yield record.name, coords

	def letters_to_coords(self,S):
		# THIS EQUATES A/T AND C/G MISMATCHES WITH NEGATIVE MATCHES, AND ALL OTHERS AS NON-MATCHES
		
		# Valid FASTQ needs quality line!
		ltc = {'A': complex(-1,0),'T': complex(1,0),'C': complex(0,-1),'G': complex(0,1)}
		return np.array([ltc.get(l, complex(0,0)) for l in S.seq]) * self.quality_to_prob(S.qual)

	def coords_to_bins(self,A,C,reverse_compliments=True):
		self.get_wheels()
		num_wheels = self.Wheels[-1]['w'] + 1
		num_spokes = self.Wheels[-1]['s'] + 1
		pow2 = np.array([2**j for j in range(num_spokes)])
		Wc = np.array([w['c'] for w in self.Wheels])
		C = np.array(C)
		L = np.dot(C,np.transpose([w['p'] for w in self.Wheels]).conjugate())
		B = [np.dot((L[:, ws:ws + num_spokes] > Wc[ws:ws + num_spokes]),pow2) for ws in range(0, num_wheels * num_spokes,num_spokes)]
		if reverse_compliments:
			L = np.dot(C[:, ::-1] * -1, np.transpose([w['p'] for w in self.Wheels]).conjugate())
			B2 = [np.dot((L[:, ws:ws + num_spokes] > Wc[ws:ws + num_spokes]),pow2) for ws in range(0, num_wheels * num_spokes,num_spokes)]
			return A, self.pick_one_from_rc_pair(B,B2)
		else:
			return A, B

	# ONLY NEED TO WRITE DOWN ONE KMER FROM REVERSE COMPLIMENT PAIR
	def pick_one_from_rc_pair(self,b1,b2,mx=1000000):
		B = [np.array([b1[i],b2[i]]) for i in range(len(b1))]
		return [b[np.mod(b,mx).argmin(0),range(b.shape[1])] for b in B]

	def quality_to_prob(self,Q):
		Q = [self.quality_codes[c] for c in Q]
		return np.array([1-10**(-q/10.) for q in Q])

	def set_wheels(self,wheels=200):
		random_kmer_path = self.input_path + 'random_kmers.fastq'
		self.quality_codes = Fq.set_quality_codes(random_kmer_path)
		Wheels = []
		for w in range(wheels):
			Wheels += self.one_wheel(w, random_kmer_path)
		Wheels.sort()
		with open(self.output_path + 'Wheels.txt','wb') as f:
			pickle.dump(Wheels,f, protocol=1)

	def get_wheels(self,spoke_limit=999,wheel_limit=999999):
		try:
			f = open(self.output_path + 'Wheels.txt', 'rb')
		except:
			f = open(self.input_path + 'Wheels.txt', 'rb')
		Wheels = pickle.load(f)
		f.close()
		# print(Wheels[0])
		self.Wheels = [{'w': x[0],'s': x[1],'p': x[2],'c': x[3]} for x in Wheels if (x[0] < wheel_limit) and (x[1] < spoke_limit)]



	def one_wheel(self,w,reads_file):
		S = []
		with Fq.open_gz(reads_file) as f:
			for s in range(self.hash_size):
				L = self.pick_leaf_noloc(self.kmer_size, f)
				P = self.affine_hull(L.values())
				C = P.pop()
				S.append((w,s,P,C))
			return S

	def pick_leaf_noloc(self,nodes,f):
		new_leaf = {}
		complex_reads = [read for read in self.generator_to_coords(Fq.fastq_generator(f, max_reads=nodes))]
		for record in complex_reads:
			new_leaf[len(new_leaf)] = list(record[1])
		return new_leaf

	def affine_hull(self,linear_system):
		# linear_system: d dimensions of n docs in this hyperplane
		linear_system = list(linear_system)
		for row in linear_system:
			row.append(-1)
		linear_system.append([0] * len(linear_system[0]))
		linear_system = np.array(linear_system)
		U,W,V = np.linalg.svd(linear_system)
		return list(V[-1,:])
