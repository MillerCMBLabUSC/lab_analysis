from lab_analysis.libs.noise import simulate
from lab_analysis.libs.compression import encoding
from lab_analysis.libs.compression import EMDCode as emd
from lab_analysis.libs.compression import delta
from lab_analysis.libs.compression import to_str as ts
import matplotlib.pyplot as plt
import numpy as np

alpha = 1.0
white_noise_sigma = 1.0
length_ts = 600
f_knee = 2.0
sample_rate = 100.0
cratio = []
realizations = 10

for i in range(realizations):
    noise = simulate.simulate_noise(alpha, white_noise_sigma, length_ts, f_knee, sample_rate)
    tNoise = np.linspace(0, len(noise) - 1, len(noise))
    tNoiseS = ts.to_str(tNoise)
    yNoiseS = ts.to_str(noise)
    (textrema, yextrema) = emd.splineEMD(noise, 30, 10, 1)
    tencode = []
    yencode = []
    a = 0
    b = 0
    for j in range(len(textrema)):
        tS = ts.to_str(delta.diff(textrema[j]))
        yS = ts.to_str(yextrema[j])
        patht = encoding.Huff(tS)
        compressedt = patht.compress()
        pathy = encoding.Huff(yS)
        compressedy = pathy.compress()
        tencode.append(compressedt[1])
        yencode.append(compressedy[1])

    for k in range(len(tencode)):
        a = len(tencode[k]) + a
        b = len(yencode[k]) + b

    c = a+b
    d = len(yNoiseS)*8 + len(tNoiseS)*8
    cratio.append((d-c)/d)

plt.hist(cratio,bins='auto')
plt.xlabel('# of 1/f noise realizations')
plt.ylabel('Compression ratio')
plt.title('Compression ratio of %s 10-minute 1/f noise realizations'%realizations)
plt.show()