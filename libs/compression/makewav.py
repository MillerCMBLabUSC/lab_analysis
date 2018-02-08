#!/usr/bin/env python3

import numpy as np
from lab_analysis.libs.noise import simulate
from lab_analysis.libs.noise import correlatenoise
import sys


alpha = 1.0
white_noise_sigma = 1.0
length_ts = 1000
f_knee = 2.0
sample_rate = 100
realizations = int(sys.argv[1])
intnoise = []
for i in range(realizations):
	intnoise=[]
	j = i + 1
	noise  = simulate.simulate_noise(alpha,white_noise_sigma, length_ts,f_knee, sample_rate)
#	uncorrelate  = correlatenoise.Correlate(30000,len(one_over_f))
#	uncorrelate.fcorrelate()
#	noise = uncorrelate.copies
	if np.max(noise) >= abs(np.min(noise)):
		scalednoise = np.int32(noise/np.max(noise) * ( 2**23) -1)
	if np.max(noise) <= abs(np.min(noise)):
		scalednoise = np.int32(noise/np.min(noise) * (2 **23) -1)

	for k  in range(len(scalednoise)):
		intnoise.append(int(scalednoise[k]))

	with open('noise%s.bin' %j,'wb') as f:
		for idx in range(len(intnoise)):
			f.write(intnoise[idx].to_bytes(3,byteorder='little',signed=True))

	with open('noise%s.txt' %j,'w') as f:
		for idx in intnoise:
			f.write("%d\n" %idx)






