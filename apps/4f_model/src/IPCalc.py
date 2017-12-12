#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Sep  8 10:51:21 2017

@author: jlashner
"""

from pylab import *
import tmm
import numpy as np
import matplotlib.pyplot as plt
import scipy.integrate as intg



"""
Constants and System Parameters
"""
#speed of light [m/s]
c =2.99792458 * 10**8
GHz = 10 ** 9





"""
Helpful functions to calculate IP / AR coating
"""




def getIP(n, d, freq, theta):
    """
    Gets IP of optical elements

    Parameters
    ----------
    n : list
        Index of refraction for each element in the stack
    d : list
        Thickness for each element in the stack
    freq : float [Hz]
        Frequency
    theta:
        Incident angle
    """
    lam_vac = c / freq * 1000.

#    lam_vac = 2.0

    s = tmm.coh_tmm('s',n, d,theta,lam_vac)
    p = tmm.coh_tmm('p',n, d,theta,lam_vac)

    return -(s['T']-p['T'])/2

def getPolAbs(n, d, freq, theta):
    """
    Gets Polarized Absorption of optical elements

    Parameters
    ----------
    n : list
        Index of refraction for each element in the stack
    d : list
        Thickness for each element in the stack
    freq : float [Hz]
        Frequency
    theta:
        Incident angle
    """

    lam_vac = c / freq * 1000.

    s = tmm.coh_tmm('s',n, d,theta,lam_vac)
    p = tmm.coh_tmm('p',n, d,theta,lam_vac)

    sA = 1 - s['T'] - s['R']
    pA = 1 - p['T'] - p['R']

    return -((sA - pA)/2)

def getBandAverage(n, d, freq, fbw, theta, divisions=100):
    """
    Gets band averaged IP of stack

    Parameters
    ----------
    n : list
        Index of refraction for each element in the stack
    d : list
        Thickness for each element in the stack
    freq :
        Band center
    fbw:
        Fractional bandwidth
    theta:
        Incident angle
    """
    flo = freq * (1. - .5 * fbw)
    fhi = freq * (1. + .5 * fbw)

    fs = np.linspace(flo, fhi, divisions)
    ips = np.array(map(lambda x : getIP(n,d,x, theta), fs))
    return trapz(ips, fs) / (fhi - flo)

def getBandAverageAbs(n, d, freq, fbw, theta, divisions=100):
    """
    Gets band averaged IP of stack

    Parameters
    ----------
    n : list
        Index of refraction for each element in the stack
    d : list
        Thickness for each element in the stack
    freq :
        Band center
    fbw:
        Fractional bandwidth
    theta:
        Incident angle
    """
    flo = freq * (1. - .5 * fbw)
    fhi = freq * (1. + .5 * fbw)

    fs = np.linspace(flo, fhi, divisions)
    ips = np.array(map(lambda x : getPolAbs(n,d,x, theta), fs))
    return trapz(ips, fs) / (fhi - flo)


def ARCoat(n, lam0):
    """
    Gets Index of refraction and thickness for AR coating

    Parameters
    ----------
    n : float
        Index of refraction of element to be coated
    lam0 : float
        Optimized Wavelength [mm]
    """
    ni= .00008
    nAR = [real(n)**(1./3) + ni*1j, real(n)**(2./3) + ni * 1j]
    dAR = map(lambda x : lam0 / (4.0 * real(x)), nAR)
    return nAR, dAR

def ARCoatOld(n, lam0):
    """
    Gets Index of refraction and thickness for AR coating

    Parameters
    ----------
    n : float
        Index of refraction of element to be coated
    lam0 : float
        Optimized Wavelength [mm]
    """

    nAR = [real(n)**(1./2)]
    dAR = map(lambda x : lam0 / (4.0 * real(x)), nAR)
    return nAR, dAR

def getWinIP(freq, fbw, theta):
    """
    Gets IP for a window

    Parameters
    ==========
    freq : float [Hz]
        Band center
    fbw : float
        Fractional Bandwidth
    theta : float [rad]
        Incident angle
    """
    n = 1.5 + .0001j
    nARwin, dARwin = ARCoat(n, 2.5)
    n_window = [1.0] + nARwin + [n] + nARwin[::-1] + [1.0]
    d_window = [Inf] + dARwin + [5.0] + dARwin[::-1] + [Inf]

    return (getBandAverage(n_window, d_window, freq, fbw, theta), \
            getBandAverageAbs(n_window, d_window, freq, fbw, theta))



def getFilterIP(freq, fbw, theta):
    """
    Gets IP for a window

    Parameters
    ==========
    freq : float [Hz]
        Band center
    fbw : float
        Fractional Bandwidth
    theta : float [rad]
        Incident angle
    """
    n = 3.1 + .00008j
    nAR, dAR = ARCoat(n, 2.5)
    n_AluminaF = [1.0] + nAR + [n] + nAR[::-1] + [1.0]
    d_AluminaF = [Inf] + dAR + [2.0] + dAR[::-1] + [Inf]
    return (getBandAverage(n_AluminaF, d_AluminaF, freq, fbw, theta), \
            getBandAverageAbs(n_AluminaF, d_AluminaF, freq, fbw, theta))



if __name__ == "__main__":


    bc = np.array([93.0 * GHz,145. * GHz]) # Band center [Hz]
    fbw = np.array([.376, .276]) #Fractional bandwidth
    flo = bc * (1 - fbw/2.)
    fhi = bc * (1 + fbw/2.)

    thetas = map(np.deg2rad, [15./2,20./2,25./2,30./2])
    
    for t in thetas:
        wIP1, fIP1 = getWinIP(bc[0], fbw[0], t)[0]*100, getFilterIP(bc[0], fbw[0], t)[0]*100
        wIP2, fIP2 = getWinIP(bc[1], fbw[1], t)[0]*100, getFilterIP(bc[1], fbw[1], t)[0]*100
        
        print "%.1f & %.3f & %.3f & %.3f & %.3f & %.3f & %.3f\\\\"%(np.rad2deg(t), wIP1, wIP2, fIP1, fIP2, wIP1 + 2 * fIP1, wIP2 + 2 * fIP2)
        
        



#    nARwin, dARwin = ARCoat(1.5, 2.5)
#    n = 1.5 + .0001j
#    n_window = [1.0] + nARwin + [n] + nARwin[::-1] + [1.0]
#    d_window = [Inf] + dARwin + [5.0] + dARwin[::-1] + [Inf]
##    
##    n = 3.1 + .00008j
##    nAR, dAR = ARCoat(n, 2.5)
##    n_AluminaF = [1.0] + nAR + [n] + nAR[::-1] + [1.0]
##    d_AluminaF = [Inf] + dAR + [2.0] + dAR[::-1] + [Inf]
##    freqs = np.linspace(flo[0], fhi[1], 100)
##    refs = []
##    for f in freqs:
##       lam = c / f * 1000
##       refs  += [tmm.coh_tmm('s',n_AluminaF, d_AluminaF, theta,lam)['R']]
##        
##    plt.plot(freqs, refs)
##    plt.show()
##
##
#    print getFilterIP(band_center[0], fbw[0], np.deg2rad(15.))
#
#    i = 1
#    theta = np.deg2rad(15.)
#    freqs = np.linspace(flo[i], fhi[i], 100)
#
#    s_array = []
#    p_array = []
#
#    for f in freqs:
#        lam = c / f * 1000
#
#        s_array  += [tmm.coh_tmm('s',n_AluminaF, d_AluminaF, theta,lam)]
#        p_array  += [tmm.coh_tmm('p',n_AluminaF, d_AluminaF, theta,lam)]
#
#    ts = np.array(map(lambda x : x['T'], s_array))
#    tp = np.array(map(lambda x : x['T'], p_array))
#    rs = np.array(map(lambda x : x['R'], s_array))
#    rp = np.array(map(lambda x : x['R'], p_array))
#    As = 1 - ts - rs
#    Ap = 1 - tp - rp

#    tsave = trapz(ts, freqs) / (fhi[i]- flo[i] )
#    tpave = trapz(tp, freqs) / (fhi[i]- flo[i] )
#    print  trapz((ts - tp)/2, freqs) / (fhi[i]- flo[i] )    
#    rsave = trapz(rs, freqs) / (fhi[i]- flo[i] )
#    rpave = trapz(rp, freqs) / (fhi[i]- flo[i] )
#    Asave = trapz(As, freqs) / (fhi[i]- flo[i] )
#    Apave = trapz(Ap, freqs) / (fhi[i]- flo[i] )
#
#    print tsave, rsave, Asave
#    print tpave, rpave, Apave
#    print .5 * (tsave - tpave), .5 * (rsave - rpave), .5 * (Asave - Apave)
#




#
#
#    ips93 = []
#    ips145 = []
#    ips93Old = []
#    ips145Old = []
#    freqs = np.linspace(90. * GHz, 160 * GHz, 50)
#
#
#
#
#    for f0 in freqs:
#        lam0 =  c / f0 * 1000.
#        nARwin, dARwin = ARCoat(1.5, lam0)
#        n_window = [1.0] + nARwin + [1.5] + nARwin[::-1] + [1.0]
#        d_window = [Inf] + dARwin + [5.0] + dARwin[::-1] + [Inf]
#        theta = np.deg2rad(30.0/2)
#        ips93 += [getBandAverage(n_window, d_window, band_center[0], fbw[0], theta)]
#        ips145 += [getBandAverage(n_window, d_window, band_center[1], fbw[1], theta)]
#
#        nARwin, dARwin = ARCoatOld(1.5, lam0)
#        n_window = [1.0] + nARwin + [1.5] + nARwin[::-1] + [1.0]
#        d_window = [Inf] + dARwin + [5.0] + dARwin[::-1] + [Inf]
#        theta = np.deg2rad(30.0/2)
#        ips93Old += [getBandAverage(n_window, d_window, band_center[0], fbw[0], theta)]
#        ips145Old += [getBandAverage(n_window, d_window, band_center[1], fbw[1], theta)]
#
#
#





