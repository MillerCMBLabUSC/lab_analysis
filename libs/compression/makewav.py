#!/usr/bin/env python3
import numpy as np
from lab_analysis.libs.noise import simulate
import sys


alpha = 1.0
white_noise_sigma = 1.0
length_ts = 100000
f_knee = 2.0
sample_rate = 100
realizations = int(sys.argv[1])

for i in range(realizations):
	j = i + 1
	noise = simulate.simulate_noise(alpha, white_noise_sigma,length_ts, f_knee, sample_rate)
	scalednoise = np.int16(noise/np.max(noise) * 32767)
	np.save('noise%s.npy' %j ,scalednoise)





