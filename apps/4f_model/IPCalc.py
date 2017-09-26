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
    
    return -((s['T']-p['T'])/(s['T']+p['T']))

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
    
    nAR = [real(n)**(1./3), real(n)**(2./3)]
    dAR = map(lambda x : lam0 / (4.0 * x), nAR)
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
    
    nAR = [real(n)**(1./3), real(n)**(2./3)]
    nAR = [real(n)**(1./2)]
    dAR = map(lambda x : lam0 / (4.0 * x), nAR)
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

    nARwin, dARwin = ARCoat(1.5, 2.5)
    n_window = [1.0] + nARwin + [1.5] + nARwin[::-1] + [1.0]
    d_window = [Inf] + dARwin + [5.0] + dARwin[::-1] + [Inf]
    
    return getBandAverage(n_window, d_window, freq, fbw, theta)

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
    nAR, dAR = ARCoat(3.1, 2.5)
    n_AluminaF = [1.0] + nAR + [3.1] + nAR[::-1] + [1.0]
    d_AluminaF = [Inf] + dAR + [2.0] + dAR[::-1] + [Inf]
    
    return getBandAverage(n_AluminaF, d_AluminaF, freq, fbw, theta) 

def getFilterIPAve(freq, fbw, theta):
    nAR, dAR = ARCoat(3.1, 2.5)
    n_AluminaF =  nAR + [3.1] + nAR[::-1] 
    d_AluminaF =  dAR + [2.0] + dAR[::-1] 
    
    distances = np.linspace(10., 20., 10)
    ips = []
    for d in distances:
        n_test = [1.0] + n_AluminaF + [1.0] + n_AluminaF + [1.0]
        d_test = [Inf] + d_AluminaF + [ d ] + d_AluminaF + [Inf]
        ips += [getBandAverage(n_test, d_test, freq, fbw, theta)]

    return mean(ips)/2
    
    

if __name__ == "__main__":
    
    
    band_center = np.array([93.0 * GHz,145. * GHz]) # Band center [Hz]
    fbw = np.array([.376, .276]) #Fractional bandwidth
    flo = band_center * (1 - fbw/2.)    
    fhi = band_center * (1 + fbw/2.)
    
    nARwin, dARwin = ARCoat(1.5, 2.5)
    n_window = [1.0] + nARwin + [1.5] + nARwin[::-1] + [1.0]
    d_window = [Inf] + dARwin + [5.0] + dARwin[::-1] + [Inf]
    
    theta = np.deg2rad(30./2)
    ips = []
    freqs = np.linspace((120 - 60) * GHz,(120 + 60)* GHz, 100)
    for f in freqs:
        ips += [getIP(n_window, d_window, f, theta)]
        
        
    nARwin, dARwin = ARCoatOld(1.5, 2.5)
    n_window = [1.0] + nARwin + [1.5] + nARwin[::-1] + [1.0]
    d_window = [Inf] + dARwin + [5.0] + dARwin[::-1] + [Inf]
    

    ipsOld = []

    for f in freqs:
        ipsOld += [getIP(n_window, d_window, f, theta)]
    
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




    
