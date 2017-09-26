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

GHz = 10 ** 9

Tcmb = 2.725


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
    return np.trapz(spec, freqs)

#Spillover efficiency
def spillEff(D, F, waistFact, freq): 
    return 1. - np.exp((-np.power(np.pi,2)/2.)*np.power((D/(waistFact*F*(c/freq))),2))


def powFrac(T1, T2, f1, f2):
        if T1==0:
            return 0
        else: 
            return bbPower(T1, 1.0, f1, f2)/bbPower(T2, 1.0, f1, f2)


def getLambdaOptCoeff(chi):
    geom = (1 / np.cos(chi) - np.cos(chi))
    return - 2 * geom * np.sqrt(4 * PI * eps0 * rho )

def getLambdaOpt(nu, chi):
    geom = (1 / np.cos(chi) - np.cos(chi))
    return - 2 * geom * np.sqrt(4 * PI * eps0 * rho * nu)

def aniPowSpec(emissivity, freq, temp=None):
        if temp == None:
            temp = Tcmb

        occ = 1.0/(np.exp(h*freq/(temp*kB)) - 1)

        return ((h**2)/kB)*emissivity*(occ**2)*((freq**2)/(temp**2))*np.exp((h*freq)/(kB*temp))


def dPdT(elements, det):
    """Conversion from Power on detector to Kcmb"""
    totalEff = lambda f : reduce((lambda x,y : x * y), map(lambda e : e.Eff(f), elements[1:]))
    print "Total Efficiency: %e"%totalEff(det.band_center)
    return intg.quad(lambda x: aniPowSpec(totalEff(x), x, Tcmb), det.flo, det.fhi)[0]
    

#***** Public Methods *****

def lamb(freq, index=None):
    """Convert from from frequency [Hz] to wavelength [m]"""
    if index == None:
        index = 1.
    
    return c/(freq*index)

def dielectricLoss( lossTan, thickness, index, freq, atmScatter=0):
    """Dielectric loss coefficient with thickness [m] and freq [Hz]"""
    return 1.0 - np.exp((-2*PI*index*lossTan*thickness)/lamb(freq/GHz))


if __name__=="__main__":
    bc = 145 * GHz
    fbw = .276
    flo = bc * (1 - fbw / 2)
    fhi = bc * (1 + fbw / 2)
    T = Tcmb

    
    #Exact
    occ = lambda nu :  1./(np.exp(h * nu / (T * kB)) - 1)
    aniSpec = lambda nu :  2 * h**2 * nu **2 / (kB * T**2) * occ(nu)**2 * np.exp(h * nu / (kB * T)) 
    factor1 = intg.quad(aniSpec, flo, fhi)[0]
    
    
    
    cumEff = .3638
    
    factor2 = 2 * kB * (fhi - flo)
    print factor1 * pW
    print factor2 * pW
    print factor2 / factor1
#    freqs = np.linspace(flo, fhi, 30)
#    plt.plot(freqs, aniSpec(freqs) / (2 * kB))
##    plt.plot(freqs, [2 * kB for f in freqs])
#    plt.show()
    

    
    
    
    
    