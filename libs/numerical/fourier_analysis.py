# spectral analysis functions:
# originally written by Hannes.
# updated by Kate, October 2013.

import numpy as np
import scipy
import scipy.signal
import pylab
import math
import copy


def window(data, window='hanning', renormalize=1):
    ''' Windows the data with hanning window
        If renormalize is set to 1, the data is multiplied by
        a factor which makes the mean squared amplitude of the
        windowed data equal to the mean squared amplitude of the
        original data.  This is important for normalizing a PSD
        correctly.
    '''
    N = len(data)
    rescale = (8/3.)**0.5  # normalize the power for a hanning window
    if renormalize == 1:
        return data*np.hanning(N)*rescale
    else:
        return data*np.hanning(N)


def fft_coefficients(timestream, samplerate=25e6 / 2 ** 16):
    ''' Calculates the fft amplitude coefficients for the input
        timestream.  timestream is a list or an array.
        data[0] = frequency
        data [1] = amplitude coefficients
        '''
    N = len(timestream)
    FFT = np.abs(np.fft.fft(timestream)[:N/2]) / N
    FFT[1:-1] *= 2
    FREQ = np.fft.fftfreq(N, 1/samplerate)[:N/2]
    return np.vstack((FREQ, FFT))


def test_fft_coefficients():
    n = 2 ** 10
    x = range(0, n)
    x = np.array(x)
    y = 10 * sin(2 * pi * x * 60 / 381.47) + random.normal(0, 1, n)
    # s/n = 10
    FFT = fft_coefficients(y)
    return FFT


def psd_func_real(timestream, sample_rate=sample_rates.bolo, truncate=False):
    '''
       Takes the power spectral density per unit time of the input timestream.
       Units: timestream_units**2/Hz
       The PSD is normalized such that sum(PSD)/total_time = variance
       For white noise, mean(PSD)*(largest_f-smallest_f) = variance
       If truncate=True, the array is truncated to the closest power of two.
       WARNING: this is a fast implentation that works for REAL tiemstream only
       Output:
        [frequencies, PSD]
    '''
    ts = timestream
    N = len(timestream)
    if truncate:
        if (N & N-1):
            a = int(math.log(N, 2))
            N = 2**a
            ts = timestream[:N]
    #rfftfreq is not supported at Minnesota, using the slightly slower fftfreq when rfftfreq is not available
    try:
        FREQ = np.abs(np.fft.rfftfreq(N, 1.0/sample_rate))
    except AttributeError:
        FREQ = np.abs(np.fft.fftfreq(N, 1.0/sample_rate)[:N/2+1])
    PSD = np.abs(np.fft.rfft(ts))**2
    norm = N**2 / (N / sample_rate)
    PSD /= norm
    PSD[1:-1] *= 2
    return np.vstack((FREQ, PSD))


def test_psd_normalization():
    ''' This function tests the normalization of function psd. Mock data is
        one second of normal, mean zero, std = 2 data sampled at
        1kHz.  Since this is white noise, the white noise level of the PSD times
        the root of the bandwidth should give the rms amplitude of the
        data (in this case rt(2)).

        The normalization for a hanning window is also tested.  Windowing
        the data removes power from the time stream.  The data must be
        recalibrated in order to recover the best estimate of the white
        noise level.  For a hanning window the time stream must be multipled by
        root(8/3) before the PSD is taken.
        '''

    # make fake data, window, window and rescale
    x = scipy.random.normal(0, 2, 10000)
    wrx = window(x, 'hanning', 1)
    ms_x = scipy.mean(x ** 2)
    ms_wrx = scipy.mean(np.array(wrx) ** 2)
    ratio = ms_x / ms_wrx
    print ('MSA of timestream = %.4f\t\nMSA of windowed timestream = %.4f\nratio = %.4f' % (ms_x, ms_wrx, ratio))
    # take PSDs
    x_psd = psd(x, 381.47)
    wrx_psd = psd(wrx, 381.47)
    pylab.subplot(2, 1, 1)
    pylab.title('Test psd normalization')
    pylab.xlabel('Sample')
    pylab.ylabel('Cnts')
    pylab.plot(x, 'bo', wrx, 'ro')
    pylab.subplot(2, 1, 2)
    pylab.title('PSD')
    pylab.xlabel('Frequency [Hz]')
    pylab.ylabel('Cnts/rtHz')
    pylab.loglog(x_psd[0], x_psd[1], 'b-', wrx_psd[0], wrx_psd[1], 'r-')
    pylab.show()
    #return PSD


def calculate_psd(timestream, rate=None, truncate=False):
    if rate is None:
        rate = sample_rates.bolo
    N = len(timestream)
    if truncate:
        if (N & N-1):
            a = int(math.log(N, 2))
            N = 2**a
    ts = scipy.signal.detrend(timestream[:N])
    ts = window(ts, 'hanning', 1)
    psd = psd_func_real(ts, rate)
    return psd
