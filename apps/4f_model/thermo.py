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
#Vacuum Permitivity
eps0 = 8.85e-12
#Resistivity of the mirror
rho=2.417e-8


#Calculates total black body power for a given temp and emis.
def bbSpec(freq,temp,emis):
	occ = 1.0/(np.exp(h*freq/(temp*kB)) - 1)

	if callable(emis):
		e = emis(freq)
	else:
		e = emis

	return (2*e*h*freq**3)/(c**2)* occ

#Calculates total black body power for a given temp and emis multiplied by the optical throughput.
def weightedSpec(freq,temp,emis):
	AOmega = (c/freq)**2
	return (AOmega*bbSpec(freq,temp,emis))

def bbPower(temp, emis, f1,f2):
	power = .5*intg.quad(lambda x: weightedSpec(x,temp,emis), f1, f2)[0]
	return power

def powFromSpec(freqs, spec):
	return .5 * np.trapz(spec, freqs)

#Spillover efficiency
def spillEff(D, F, waistFact, freq): 
	return 1. - np.exp((-np.power(np.pi,2)/2.)*np.power((D/(waistFact*F*(c/freq))),2))


def powFrac(T1, T2, f1, f2):
		if T1==0:
			return 0
		else: 
			return bbPower(T1, 1.0, f1, f2)/bbPower(T2, 1.0, f1, f2)


def getLambdaOpt(nu, chi):
	geom = (1 / np.cos(chi) - np.cos(chi))
	return - 2 * geom * np.sqrt(4 * PI * eps0 * rho * nu)