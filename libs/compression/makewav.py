import numpy as np
from lab_analysis.libs.noise import simulate
from tempfile import TemporaryFile

alpha = 1.0
white_noise_sigma = 1.0
length_ts = 10000000
f_knee = 2.0
sample_rate = 44100
noise = simulate.simulate_noise(alpha, white_noise_sigma,length_ts, f_knee, sample_rate)
scalednoise = np.int16(noise/np.max(noise) * 32767)
Fs = 44100
f = 440
sample = 44100
duration = 1
x = np.arange(Fs * duration)
y = (np.sin(2 * np.pi * np.arange(Fs * duration) * f / Fs))
scaledy = np.int16(y/np.max(y)*32767)
outfile = TemporaryFile()
np.save('noise.npy',scalednoise)





