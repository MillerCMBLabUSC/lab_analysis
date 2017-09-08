#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  2 18:41:36 2017

@author: gteply
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

	s = tmm.coh_tmm('s',n, d,theta,lam_vac)
	p = tmm.coh_tmm('p',n, d,theta,lam_vac)
    
	return -((s['T']-p['T'])/(s['T']+p['T']))

def getBandAverage(n, d, bid, divisions=100):
	fs = np.linspace(flo[bid], fhi[bid], divisions)
	ips = np.array(map(lambda x : getIP(n,d,x), fs))
	return trapz(ips, fs) / (fhi[bid] - flo[bid])

def ARCoat(n, lam):
    nAR = [real(n)**(1./3), real(n)**(2./3)]
#    nAR = [real(n)**(1./2)]
    dAR = map(lambda x : lam / (4.0 * x), nAR)
    return nAR, dAR

"""
Indices of refraction and thicknesses [mm] of optical elements
"""
lam0 = 2.5 #[mm]
nwin = 1.5 
dwin = 5.0
nARwin, dARwin = ARCoat(nwin, lam0)
n_window = nARwin + [nwin] + nARwin[::-1]
d_window = dARwin + [dwin] + dARwin[::-1]

print n_window
print d_window


n_styrofoam = [1.03,1.0,1.03,1.0,1.03,1.0,1.03,1.0,1.03,1.0,1.03,1.0,1.03,1.0,1.03,1.0,1.03,1.0,1.03]
d_styrofoam = [3.0,0.5,3.0,0.5,3.0,0.5,3.0,0.5,3.0,0.5,3.0,0.5,3.0,0.5,3.0,0.5,3.0,0.5,3.0]



n0 = 3.1
lam0 = 2.5
d_filter = 2.0
nAR, dAR = ARCoat(n0, lam0)
n_AluminaF = nAR + [n0] + nAR[::-1]
d_AluminaF = dAR + [d_filter] + dAR[::-1]





"""
Constructing optical chains
"""
#Construction of the optical chain
n_fullChain = [1.0] + n_window + [ 1.0] + n_styrofoam + [1.0] + n_AluminaF + [1.0] + n_AluminaF + [1.0]
d_fullChain = [Inf] + d_window + [50.0] + d_styrofoam + [0.5] + d_AluminaF + [2] + d_AluminaF + [Inf]


#n_test= [1.0] + n_window + [ 1.0] 
#d_test= [Inf] + d_window + [Inf]
#
#
#print getBandAverage(n_test, d_test, 0)


#print 

distances = np.linspace(0,30,300)
ips = [[] for _ in band_center]
for bid in range(len(band_center)):
    print "Calculating IP for %d GHz"%(band_center[bid] / GHz)
    for d in distances: 
        n_test = np.array([1.0] + n_AluminaF + [1.0] + n_AluminaF + [1.0])
        d_test = np.array([Inf] + d_AluminaF + [ d] + d_AluminaF + [Inf])
        ips[bid] += [getBandAverage(n_test, d_test, bid)]

# distances = np.linspace(0,20,300)
# ips = [[],[]]
# for bid in [0,1]:
# 	for d in distances:
# 		n_test = np.array([1.0] + n_AluminaF + [1.0] + n_AluminaF + [1.0])
# 		d_test = np.array([Inf] + d_AluminaF + [ d] + d_AluminaF + [Inf])
			
# 		ips[bid] += [getBandAverage(n_test, d_test, bid)]

# print mean(ips[0][200:])
# plt.plot(distances, ips[0])
# plt.show()
# plt.plot(distances, ips[1])

# plt.xlabel("Gap (mm)")
# plt.ylabel("IP")
# plt.legend(['93 GHz', '150 GHz'])
# # plt.title('IP vs. gap between Aluminum Filter')
# plt.tight_layout()
# plt.savefig('ip_vs_gap_filter_only.png')
# plt.clf()