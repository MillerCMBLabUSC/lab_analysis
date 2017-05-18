import scipy.integrate as intg
import numpy as np

#Physical Constants
#Everything is in MKS units
#Planck constant [J/s]
h = 6.6261e-34
#Boltzmann constant [J/K]
kB = 1.3806e-23
#Speed of light [m/s]
c = 299792458.0
#Pi
PI = 3.14159265

#Calculates total black body power for a given temp and emis.
def weightedSpec(freq,temp,emis):
	occ = 1.0/(np.exp(h*freq/(temp*kB)) - 1)
	AOmega = (c/freq)**2
	return (AOmega*(2*emis*h*freq**3)/(c**2)* occ)


def bbPower(temp, emis, f1,f2):
	power = .5*intg.quad(lambda x: weightedSpec(x,temp,emis), f1, f2)[0]
	return power