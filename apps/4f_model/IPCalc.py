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


band_center = np.array([93.0 * GHz,150. * GHz]) # Band center [Hz]
fbw = np.array([.376, .276]) #Fractional bandwidth
flo = band_center * (1 - fbw/2.)    
fhi = band_center * (1 + fbw/2.)

theta=deg2rad(15./2) #incident angle

"""
Helpful functions to calculate IP / AR coating
"""

def getIP(n, d, freq):
    lam_vac = c / freq * 1000.
    
#    lam_vac = 2.0

    s = tmm.coh_tmm('s',n, d,theta,lam_vac)
    p = tmm.coh_tmm('p',n, d,theta,lam_vac)
    
    return -((s['T']-p['T'])/(s['T']+p['T']))

def getBandAverage(n, d, bid, divisions=100):
    fs = np.linspace(flo[bid], fhi[bid], divisions)
    ips = np.array(map(lambda x : getIP(n,d,x), fs))
    return trapz(ips, fs) / (fhi[bid] - flo[bid])

def ARCoat(n, lam0):
    nAR = [real(n)**(1./3), real(n)**(2./3)]

    dAR = map(lambda x : lam0 / (4.0 * x), nAR)
    return nAR, dAR




if __name__ == "__main__":
    
    nARwin, dARwin = ARCoat(1.5, lam0)
    n_window = nARwin + [1.5] + nARwin[::-1]
    d_window = dARwin + [5.0] + dARwin[::-1]
        
    n_styrofoam = [1.03] + [1.0, 1.03] * 9
    d_styrofoam = [3.0] + [0.5, 3.0] * 9
    
    nAR, dAR = ARCoat(3.1, lam0)
    n_AluminaF = nAR + [3.1] + nAR[::-1]
    d_AluminaF = dAR + [2.0] + dAR[::-1]
    
    #Construction of the optical chain
    n_fullChain = [1.0] + n_window + [ 1.0] + n_styrofoam + [1.0] + n_AluminaF + [1.0] + n_AluminaF + [1.0]
    d_fullChain = [Inf] + d_window + [50.0] + d_styrofoam + [0.5] + d_AluminaF + [2] + d_AluminaF + [Inf]   

    freqs = np.linspace(90 * GHz, 150 * GHz, 60)
    ips = [[] for _ in band_center]
    for bid in [0,1]:
        print "Band %d"%(bid)
        for f0 in freqs:
            
            lam0 = c / f0 * 1000
            
            nARwin, dARwin = ARCoat(1.5, lam0)
            n_window = [1.0] + nARwin + [1.5] + nARwin[::-1] + [1.0]
            d_window = [Inf] + dARwin + [5.0] + dARwin[::-1] + [Inf]
            
            ips[bid] += [getBandAverage(n_window, d_window, bid)]
            














