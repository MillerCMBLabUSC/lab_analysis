import numpy as np
import thermo as th
from scipy import interpolate
from scipy import integrate as intg
import matplotlib.pyplot as plt

import Detector as dt
import IPCalc


# Units and Constants
GHz = 1.e9 # GHz -> Hz
pW = 1.e12 # W -> pW


eps0 = 8.85e-12 #Vacuum Permitivity
rho=2.417e-8 #Resistivity of the mirror


class OpticalElement:
    """ Optical Element
        *****
        Optional Parmeters:
            :Thick: Thickness [mm]
            :Index: Index of refraction
            :LossTan: Loss Tangent
            :Absorb: Absorption Coefficient
            :Refl: Reflection coefficient
            :Spill: Spillover Fraction
            :ScattFrac: Scattered Fraction
            :ScattTemp: Scattered Temperature
            :SpillTemp: Spillover Temperature
            :IP: IP value
            :PolAbs: Polarized Absorption Coefficient
            :Chi: Incident angle of Mirror
            :Freqs: Frequency Array for 
            :EffCurve: Efficiency Function (Corresponding to frequency array)
            :IPCurve: IP Function
            :EmisCurve: Emission Function
    """
    def __init__(self, name, det, temp, params = {}):
        self.name = name
        self.det = det
        self.temp = temp
        
        #Sets Default Optical Element Parameters
        self.params = {"Thick": 0,      "Index": 0, "LossTan": 0, "Absorb": 0, \
                       "Absorb": 0,     "Spill": 0, "SpillTemp": 0, "Refl": 0, "ScattFrac": 0, \
                       "ScattTemp": 0,  "IP": 0, "PolAbs": 0,  "Chi": 0, \
                       "Freqs": None,   "EffCurve": None, "IPCurve": None, "EmisCurve": None, "PolEmisCurve": None};
        
        #Sets input parameters                       
        for k in params.keys():
            p = params[k]
            if type(p) !=  np.string_:
                self.params[k]= p
            else:

                try:
                    #Converts to float if input is a string
                    v = eval(params[k])
                    if type(v) == list:
                        self.params[k] = v[self.det.bid - 1]
                    else:
                        self.params[k] = v
                except:
                    if params[k] == "NA":
                        self.params[k] = 0

    def updateParams(self, modifiedParams):
        self.params.update(modifiedParams)
    
    
    #IP Coefficient 
    def Ip(self, freq):
        if self.params["IPCurve"] is not None:
            return np.interp(freq, self.params["Freqs"], self.params["IPCurve"])
        return self.params["IP"]
    
    #Absorption coefficient
    def Absorb(self, freq):
        if self.params["LossTan"] != 0:
            return th.dielectricLoss(self.params["LossTan"], self.params["Thick"], self.params["Index"], freq)
        else:
            return self.params["Absorb"]
    
    #Transmission Coefficient
    def Eff(self, freq):
        if self.params["EffCurve"] is not None:
            return np.interp(freq, self.params["Freqs"], self.params["EffCurve"])
        elif self.name == "Aperture":
            return th.spillEff(self.det)
        else:
            return  1 - self.Absorb(freq) - self.params["Spill"]- self.params["Refl"]
            
    #Polarized Efficiency
    def pEff(self, freq):
        return self.Eff(freq)

    def Emis(self, freq):
        if self.params["EmisCurve"] is not None:
            return np.interp(freq, self.params["Freqs"], self.params["EmisCurve"])
        if self.name == "Atm":
            # Returns 1 because we are using Rayleigh Jeans temperature
            return 1
        
        if self.params["Spill"] != 0:
            spillEmis = self.params["Spill"] * th.powFrac(self.params["SpillTemp"], self.temp, self.det.flo, self.det.fhi)
        else:
            spillEmis = 0
            
        if self.name == "Aperture":
            return (1 - self.Eff(freq) + spillEmis)
        else:
            return self.Absorb(freq) + spillEmis

    #Polarized Emissivity
    def pEmis(self, freq):
        if self.params["PolEmisCurve"] is not None:
            return np.interp(freq, self.params["Freqs"], self.params["PolEmisCurve"])        
        
        if self.name == "Mirror":
            return - self.Ip(freq)
        
        if self.name == "HWP":
            ao = 8.7*10**(-5) * (freq/ GHz) + 3.1*10**(-7)*(freq/GHz)**2 + (3.0)*10**(-10) * (freq/GHz)**3 #1/cm
            ae = 1.47*10**(-7) * (freq/GHz)**(2.2) #1/cm
            Eotrans =  np.exp(self.params["Thick"]/10.0 * ao * self.temp/300) 
            Eetrans =  np.exp(self.params["Thick"]/10.0 * ae * self.temp/300)
            
            pemis = (abs(Eetrans)**2 - abs(Eotrans)**2) / 2            
            return pemis
        
        return self.params["PolAbs"]



def loadAtm(atmFile, det):
    """Loads an optical element from specified atmosphere file"""
    freqs, temps, trans = np.loadtxt(atmFile, dtype=np.float, unpack=True, usecols=[0, 2, 3]) #frequency/tempRJ/efficiency arrays from input files
    freqs*=GHz # [Hz]
    
    atmTemp = 300. # [K]
    emis = temps / atmTemp
    e = OpticalElement("Atm", det, atmTemp, {"Freqs": freqs, "EffCurve": trans, "EmisCurve": emis})
    return e
    
    
    #Reads Rayleigh Jeans temperature from file and takes average
#    tempF = interpolate.interp1d(freqs, temps, kind = "linear")
#    x = np.linspace(det.flo, det.fhi, 400)
#    y = tempF(x)
#    aveTemp = intg.simps(y, x=x)/(det.fhi - det.flo)
#    e = OpticalElement("Atm", det, aveTemp, {"Freqs": freqs, "EffCurve": trans})
#    
#    return e

def loadOpticalChain(opticsFile,det, theta = np.deg2rad(15./2)):
    """Returns list of optical elements from opticalChain.txt file. """
    
    data = np.loadtxt(opticsFile, dtype=np.str)
    keys = data[0]

    elements = []
    
    for line in data[1:]:
        params = dict(zip(keys, line))
        name = params["Element"]        
        
        if name == "AluminaF":
            (ip, polAbs) = IPCalc.getFilterIP(det.band_center, det.fbw, theta)
            params.update({"IP": ip, "PolAbs": polAbs})
        elif name == "Window": 
            (ip, polAbs) = IPCalc.getWinIP(det.band_center, det.fbw, theta)
            params.update({"IP": ip, "PolAbs": polAbs})

        e = OpticalElement(name, det, eval(params["Temp"]), params = params)
        elements.append(e)

    return elements

