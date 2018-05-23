import simulate
import encoding
import EMDCode as emd
import delta
import to_str as ts
from bitstring import BitArray, BitStream
#from lab_analysis.libs.noise import simulate
#from lab_analysis.libs.compression import encoding
#from lab_analysis.libs.compression import EMDCode as emd
#from lab_analysis.libs.compression import delta
#from lab_analysis.libs.compression import to_str as ts
import matplotlib.pyplot as plt
import numpy as np
import pickle

alpha = 1.0
white_noise_sigma = 1.0
length_ts = 600
f_knee = 2.0
sample_rate = 100.0
cratio = []
realizations = 1

for i in range(realizations):
    #noise = np.load(open('69_calib.npy','rb',encoding='utf-8'))[0:100]
    noise = open('69.txt','r').read().split('\n')[0:59]
    
    noise = [float(i) for i in noise]
    
    #noise = simulate.simulate_noise(alpha, white_noise_sigma, length_ts, f_knee, sample_rate)
    #tNoise = np.linspace(0, len(noise) - 1, len(noise))
    #tNoiseS = ts.to_str(tNoise)
    yNoiseS = ts.to_str(noise)
    (textrema, yextrema) = emd.splineEMD(noise, 40, 10, 1)
    yencode = []
    #a = 0
    b = 0
    for j in range(len(yextrema)):
        #tS = ts.to_str(delta.diff(textrema[j]))
        yS = ts.to_str(yextrema[j])
        print(yS)
        #patht = encoding.Huff(tS)
        #compressedt = patht.compress()
        pathy = encoding.Huff(yS)
        compressedy = pathy.compress()
        #tencode.append(compressedt[1])
        yencode.append(compressedy[1])

    for k in range(len(yencode)):
        #print(k)
        #a = len(tencode[k]) + a
        b = len(yencode[k]) + b

    #c = a+b
    #d = len(yNoiseS)*8 + len(tNoiseS)*8
    #cratio.append((d-c)/d)
    ratio = (len(yNoiseS)*8 - b)/(len(yNoiseS)*8)
    thefile = open('69_chunk_compressed.bin', 'wb')
    for item in yencode:
        s = ''.join(item)
        b = BitArray(bin=s)
        thefile.write(b.tobytes())
    thefile.close()
    thefile = open('69_chunk.txt', 'w')
    for item in noise:
        thefile.write("%s\n" %item)
    thefile.close()
#plt.hist(cratio,bins='auto')
#plt.xlabel('# of 1/f noise realizations')
#plt.ylabel('Compression ratio')
#plt.title('Compression ratio of %s 10-minute 1/f noise realizations'%realizations)
#plt.show()
#print(yencode)
print(ratio)
