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


#speed of light [m/s]
c =2.99792458 * 10**8
GHz = 10 ** 9

band_center = np.array([93.0 * GHz, 150. * GHz])
fbw = np.array([.376, .276])

flo = band_center * (1 - fbw/2.)
fhi = band_center * (1 + fbw/2.)
# print flo, fi
theta=deg2rad(15./2)

def getIP(n, d, freq):
	lam_vac = c / freq * 1000.

	s = tmm.coh_tmm('s',n, d,theta,lam_vac)
	p = tmm.coh_tmm('p',n, d,theta,lam_vac)


	return -((s['T']-p['T'])/(s['T']+p['T']))

def getBandAverage(n, d, bid, divisions=100):
	fs = np.linspace(flo[bid], fhi[bid], divisions)
	ips = np.array(map(lambda x : getIP(n,d,x), fs))
	return trapz(ips, fs) / (fhi[bid] - flo[bid])



#Indices of refraction and thicknesses [mm] of optical elements

n_window = [sqrt(1.5),1.5+0.0001j,sqrt(1.5)]
d_window = [0.25*2.0/sqrt(1.5),5.0,0.25*2.0/sqrt(1.5)]

n_styrofoam = [1.03,1.0,1.03,1.0,1.03,1.0,1.03,1.0,1.03,1.0,1.03,1.0,1.03,1.0,1.03,1.0,1.03,1.0,1.03]
d_styrofoam = [3.0,0.5,3.0,0.5,3.0,0.5,3.0,0.5,3.0,0.5,3.0,0.5,3.0,0.5,3.0,0.5,3.0,0.5,3.0]

n0 = 3.1
lam0 = 2.5
n_AluminaF = [n0**(1./3), n0**(2./3), n0 + .00008j, n0**(2./3), n0**(1./3)]
# d_AluminaF = [0.25*2.0/sqrt(3.1),2.0,0.25*2.0/sqrt(3.1)]

d_AluminaF = [lam0/(4.0*real(n0)**(1./3)), lam0/(4.0*real(n0)**(2./3)), 2.0, \
			  lam0/(4.0*real(n0)**(2./3)), lam0/(4.0*real(n0)**(1./3))]

#Construction of the optical chain
n_fullChain = [1.0] + n_window + [ 1.0] + n_styrofoam + [1.0] + n_AluminaF + [1.0] + n_AluminaF + [1.0]
d_fullChain = [Inf] + d_window + [50.0] + d_styrofoam + [0.5] + d_AluminaF + [10] + d_AluminaF + [Inf]

n_test = [1.0] + n_AluminaF + [1.0] + n_AluminaF  + [1.0]
d_test = [Inf] +  d_AluminaF + [10] + d_AluminaF  + [Inf]


distances = np.linspace(15,20,100)
ips = [[],[]]
for bid in [0,1]:
	for d in distances:
		n_test = np.array([1.0] + n_AluminaF + [1.0] + n_AluminaF + [1.0])
		d_test = np.array([Inf] + d_AluminaF + [ d] + d_AluminaF + [Inf])
			
		ips[bid] += [getBandAverage(n_test, d_test, bid)]



print "93 GHz average: %e"%(mean(ips[0])/2)
print "150 GHz average: %e"%(mean(ips[1])/2)

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