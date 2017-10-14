#!/usr/bin/env python

import sys
import argparse
import glob
import os
import json

# MergeHash can maybe go on the hour queue
# adjust cluster thresh (-t) as necessary
# number of tasks is 2**hash_size/10**6 + 1
# !!!
# adjust cluster thresh (-t) as necessary - probably same as Index step (maybe slightly higher)
# !!!
# MAKE SURE TO SET TMP FILE LOCATION
# Check to make sure there are no files remaining in cluster_vectors/PARTITION_NUM/

# FUNC
def interface():
    parser = argparse.ArgumentParser(description="Creates jobs.")

    parser.add_argument('-j',
                        required=True,
                        dest='JOB',
                        type=str,
                        metavar='<job_name>',
                        help='Name of the Job to be executed.')    

    parser.add_argument('-i',
                        required=True,
                        dest='IN',
                        type=str,
                        metavar='<input_dir>',
                        help='Input directory for job.')

    

    args = parser.parse_args()
    return args

# MAIN
if __name__ == "__main__":
	args = interface()

	job = args.JOB

	input_dir = args.IN
	if not input_dir.endswith('/'):
		input_dir += '/'

	script_dir = os.path.dirname(__file__)
	with open(script_dir + '/job_config.json', 'r') as f:
		config = json.load(f)
		JobParams = config['JobParams']
		CommonElements = config['CommonElements']

	try:
		params = JobParams[job]
	except KeyError:
		print('\n"' + job + '" is not a valid job name. Known jobs are:')
		print('\n'.join([jobs for jobs in JobParams.keys()]) + '\n')
		raise 


	if params.get('array',None) != None:
		FP = glob.glob(os.path.join(inputdir+params['array'][0],params['array'][1]))
		if len(params['array']) == 3:
			FP = [fp[fp.rfind('/')+1:] for fp in FP]
			if params['array'][2] == -1:
				suffix = params['array'][1].replace('*','').replace('.','')
				FP = set([fp[:fp.index(suffix)] for fp in FP])
			else:
				FP = set([fp[:fp.index('.')] for fp in FP])
			FP = [None]*len(FP)*abs(params['array'][2])
		array_size = str(len(FP))
		params['header'][0] += array_size+']'
		print(job+' array size will be '+array_size)
	f = open(inputdir+'LSFScripts/'+params['outfile'],'w')
	f.write('\n'.join(CommonElements['header']) + '\n')
	f.write('\n'.join(params['header']).replace('PROJECT_HOME/',inputdir) + '\n')
	f.write('\n'.join(CommonElements['body']) + '\n')
	f.write('\n'.join(params['body']).replace('PROJECT_HOME/',inputdir) + '\n')
	f.write('\n'.join(CommonElements['footer']) +'\n')
	f.close()
	