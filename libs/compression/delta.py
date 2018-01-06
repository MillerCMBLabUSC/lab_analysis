import numpy as np


def diff(array):
    first = [array[0]]
    _diff=np.ediff1d(array)
    difference = np.append(first,_diff)

    return difference

if __name__ == "__main__":
    from lab_analysis.libs.noise import simulate
    from lab_analysis.libs.compression import EMDCode as emd
    alpha = 1.0
    white_noise_sigma = 1.0
    length_ts = 1000
    f_knee = 2.0
    sample_rate = 100.0
    noise = simulate.simulate_noise(alpha, white_noise_sigma, length_ts, f_knee, sample_rate)
    (textrema,yextrema) = emd.splineEMD(noise,30,10,1)
    diff_t = []
    diff_y = []
    for i in range(len(textrema)):
        diff_t.append(diff(textrema[i]))
        diff_y.append(diff(yextrema[i]))

    print(yextrema)
    print(diff_y)

