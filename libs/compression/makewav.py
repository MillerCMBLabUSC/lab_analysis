import numpy as np
from scipy.io.wavfile import write
from lab_analysis.libs.noise import simulate
import matplotlib.pyplot as plt
Fs = 44100
f = 440
sample = 44100
duration = 5
x = np.arange(Fs*duration)
y =(np.sin(2*np.pi*np.arange(Fs*duration)*f/Fs))
scaledy = np.int16(y/np.max(np.abs(y)) * 32767)
alpha = 1.0
white_noise_sigma = 1.0
length_ts = 600
f_knee = 2.0
sample_rate = 44100
noise = simulate.simulate_noise(alpha, white_noise_sigma,length_ts, f_knee, sample_rate)
scalednoise = np.int16(y/np.max(np.abs(y)) * 32767 )
write("noisewav.wav",sample_rate,scalednoise)