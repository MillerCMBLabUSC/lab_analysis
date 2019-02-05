import numpy as np

for i in range(100):
    data = np.load('timestream%s.npy' %i)
    #data = data[:1400]
    timestream = []

    N = len(data)

    for k in range(N):
        timestream.append(int(data[k]))

    with open('timestream%s.bin' %i, 'wb') as f:
        for dx in range(len(data)):
            f.write(timestream[dx].to_bytes(4,byteorder='little',signed=True))
