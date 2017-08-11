import scipy.stats
import numpy as np

def simulate_noise(alpha, white_noise_sigma, length_ts, f_knee, sample_rate, add_hwp_peaks=False, hwp_peak_amplitudes={}):
    """
    Simulates a timestream of noise. The noise is the sum of an FFT with shape 
              1/(f**alpha) until f_knee + white noise shape at frequencies > f_knee.
    Inputs:
        @ alpha (float): value such that the low frequency PSD is modelled by (1/f**[2*alpha])
        @ f_knee (float): frequency (Hz) at which the PSD turns from 1/f to white noise
        @ white_noise_sigma (float): std of the white noise. 
              this corresponds to sqrt(white_noise_level) in the PSD
        @ length_ts (int): length of returned timestream
        @ add_hwp_peaks (bool): Do you want to simulate leftover template peaks in the simulated timestreams?
        @ hwp_peak_amplitudes (dict): each key is the harmonic number, 
          each value the height of the peak of the harmonic in fft units
    Outputs:
        @ simulated_noise (array): simulated noise with length length_ts
    """
    white_noise = scipy.stats.norm.rvs(scale=white_noise_sigma, size=length_ts)
    white_noise_fft = np.fft.rfft(white_noise)
    delta_t = 1.0/sample_rate
    frequencies = np.fft.fftfreq(white_noise.size, delta_t)[: white_noise_fft.size]
    frequencies[-1] = np.abs(frequencies[-1])
    simulated_fft = white_noise_fft*one_over_f(frequencies, alpha, f_knee)
    if add_hwp_peaks:
        for n in hwp_peak_amplitudes.keys():
            freq = n*1.234
            index = np.argmin(abs(frequencies-freq))
            simulated_fft[index] = hwp_peak_amplitudes[n]
    simulated_noise = np.fft.irfft(simulated_fft)
    if simulated_noise.size != length_ts:
        simulated_noise = np.concatenate((simulated_noise, [simulated_noise[-1]]))
    return simulated_noise

def one_over_f(frequencies, alpha, f_knee):
    a = np.ones(frequencies.size)
    select = (0 < frequencies) & (frequencies < f_knee)
    if f_knee > 0.0:
        a[select] = np.abs((frequencies[select]/f_knee)**(-alpha))
    a[0] = 1
    return a

if __name__ == "__main__":
    import pylab as pl
    from lab_analysis.libs.numerical import fourier_analysis
    alpha = 1.0
    white_noise_sigma = 1.0
    length_ts = 5000
    f_knee = 2.0
    sample_rate = 100.0 # Hz
    noise = simulate_noise(alpha, white_noise_sigma, length_ts, f_knee, sample_rate)
    pl.subplot(211)
    pl.plot(noise)
    pl.xlabel('index (sample rate = %f Hz' %sample_rate)
    pl.ylabel("signal")
    pl.grid()
    pl.subplot(212)
    pl.loglog(*fourier_analysis.calculate_psd(noise, rate=sample_rate))
    pl.xlabel('Frequency (Hz)')
    pl.ylabel('unit^2/Hz')
    pl.grid()
    pl.show()
