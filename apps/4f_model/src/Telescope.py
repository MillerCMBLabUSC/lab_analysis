
import numpy as np
import thermo as th
import OpticalElement as opt
import Detector as dt
import propSpectrum as ps
import matplotlib.pyplot as plt
import glob as gb

#########################################################
#   Input Data                                             
#########################################################


# Units and Constants
GHz = 1.e9 # GHz -> Hz
pW = 1.e12 # W -> pW

class Telescope:
    def __init__(self, expDir, atmFile, hwpFile, bandID, theta = None, writeFile = False):
        
        channelFile = expDir + "channels.txt"
        cameraFile = expDir + "camera.txt"
        opticsFile = expDir + "opticalChain.txt"
        
        
        #Imports detector data 
        self.det = dt.Detector(channelFile, cameraFile, bandID)
        self.freqs = np.linspace(self.det.flo, self.det.fhi, 400) #Frequency array of the detector
        
        """
            Creating the Optical Chain
        """
        self.elements = [] #List of optical elements
    
        #CMB Element
        self.elements.append(opt.OpticalElement("CMB", self.det, 2.725, {"Absorb": 1}))
        
        #Atm Element
        self.elements.append( opt.loadAtm(atmFile, self.det))
        
        #Telescope elements
        self.elements += opt.loadOpticalChain(opticsFile, self.det, theta=theta)
        
        self.elements.append(opt.OpticalElement("Detector", self.det, self.det.bath_temp, {"Absorb": 1 - self.det.det_eff}))
        

        try:
            self.hwpIndex = [e.name for e in self.elements].index("HWP")
        except:
            print "No HWP in Optical Chain"
        
        
        fs, T, rho, _, _ = np.loadtxt(hwpFile, dtype=np.float, unpack=True)
        self.elements[self.hwpIndex].updateParams({"Freqs": fs, "EffCurve": T, "IPCurve": rho})
        
        
        
        self.dPdT = th.dPdT(self.elements, self.det)
        
        
##        e = opt.OpticalElement()
##        e.load("CMB", 2.725, 1)
##        self.elements.append(e)
#        
#        #Atmosphere Element
#        e = opt.OpticalElement()
#        e.loadAtm(atmFile,self.det)
#        self.elements.append(e)
#    
#        #Telescope elements
#        self.elements += opt.loadOpticalChain(opticsFile, self.det, theta=theta)
#    
#        #Detector Element
#        e = opt.OpticalElement()
#        e.load("Detector", self.det.bath_temp, 1 - self.det.det_eff)
#        self.elements.append(e) 

    
        #Gets HWP index

        


        
        self.propSpectrum()
        self.geta2()
        self.getA2()
        self.geta4()
        self.getA4()
                 
    def cumEff(self, index, freq):
        cumEff = 1.
        for i in range(index + 1, len(self.elements)):
            cumEff *= self.elements[i].Eff(freq)
        
        return cumEff
        
        
    def propSpectrum(self):
        self.UPspecs = [np.zeros(len(self.freqs))]  #Unpolarized spectrum before each element
        
        for (i, el) in enumerate(self.elements):
            
            UPEmitted = th.weightedSpec(self.freqs, el.temp, el.Emis)
            UPTransmitted = self.UPspecs[-1] * map(el.Eff, self.freqs)
            
            self.UPspecs.append(UPEmitted + UPTransmitted)
        
    def geta2(self):
        hwp= self.elements[self.hwpIndex]
        self.a2 = abs(np.trapz(map(hwp.Ip, self.freqs), self.freqs) / (self.det.fhi -self.det.flo))
        
    def getA2(self):
        hwp = self.elements[self.hwpIndex]
#        ppEmitted = np.array([0 for _ in self.freqs])
        ppEmitted = th.weightedSpec(self.freqs, hwp.temp, hwp.pEmis)
        ppTransmitted = map(hwp.Ip, self.freqs)*self.UPspecs[self.hwpIndex]
        
        print "emitted: ", th.powFromSpec(self.freqs, ppEmitted*map(lambda x : self.cumEff(self.hwpIndex, x), self.freqs))/self.dPdT
        print "transmitted: ", th.powFromSpec(self.freqs, ppTransmitted*map(lambda x : self.cumEff(self.hwpIndex, x), self.freqs))/self.dPdT
        
        self.A2 = .5 * abs(th.powFromSpec(self.freqs, (ppEmitted + ppTransmitted)* map(lambda x : self.cumEff(self.hwpIndex, x), self.freqs)) )
        
    def geta4(self):
        self.a4 = 0
        for e in self.elements:
            if e.name == "HWP":
                break
            self.a4 += e.Ip(self.det.band_center)
        
    def getA4(self):
        self.A4 = 0
        for (i, e) in enumerate(self.elements):
            if e.name=="HWP":
                break
            
            ppEmitted = th.weightedSpec(self.freqs, e.temp, e.pEmis)
            ppTransmitted = map(e.Ip, self.freqs)*self.UPspecs[i]
            ppTotal = .5 * abs(th.powFromSpec(self.freqs, (ppEmitted + ppTransmitted)* map(lambda x : self.cumEff(i, x), self.freqs)))
#            if ppTotal!=0:
#                print e.name, ppTotal*pW
            self.A4 += ppTotal
            
    




if __name__=="__main__":
    expDir = "../Experiments/small_aperture/LargeTelescope/"    
    atmFile = "Atacama_1000um_60deg.txt"    
    theta = 20
    hwpFile = "../HWP_Mueller/Mueller_AR/Mueller_V2_nu150.0_no3p068_ne3p402_ARcoat_thetain%d.0.txt"%theta
    bid = 2
    
    opts = {'theta': np.deg2rad(theta)}
    
    tel = Telescope(expDir, atmFile, hwpFile, bid, **opts)