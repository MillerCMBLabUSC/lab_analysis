from lab_analysis.libs.noise import simulate
from lab_analysis.libs.compression import discreteMinMax
from lab_analysis.libs.compression import encoding
import matplotlib.pyplot as plt

alpha = 1.0
white_noise_sigma = 1.0
length_ts = 600
f_knee = 2.0
sample_rate = 100.0
cratio = []

for i in range(50):
    noise = simulate.simulate_noise(alpha, white_noise_sigma, length_ts, f_knee, sample_rate)
    (dmin,dmax) = discreteMinMax.discreteMinMax(noise)
    noise = noise.tolist()
    noise = ''.join(str(e) for e in noise)
    dmin = dmin.tolist()
    dmin = ''.join(str(e) for e in dmin)
    path = encoding.Huff(dmin)
    compressed = path.compress()
    a = len(noise)*8
    b = len(compressed[1])
    cratio.append((a-b)/a)

plt.plot(cratio)
plt.show()