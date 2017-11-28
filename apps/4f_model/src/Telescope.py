
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
    def __init__(self, expDir, atmFile,hwpFile, bandID, \
                 hwpi = None, lensIP = None, theta = None, writeFile = False,     \
                        printChain = False \
                ):
        
        channelFile = expDir + "channels.txt"
        cameraFile = expDir + "camera.txt"
        opticsFile = expDir + "opticalChain.txt"
        
        
        
        baseDir = "/Users/jacoblashner/so/lab_analysis/apps/4f_model/"
        
        #Imports detector data 
        self.det = dt.Detector(channelFile, cameraFile, bandID)
    
        """
            CREATES OPTICAL CHAIN
        """
        self.elements = [] #List of optical elements
    
        #CMB Element
        e = opt.OpticalElement()
        e.load("CMB", 2.725, 1)
        self.elements.append(e)
        
        #Atmosphere Element
        e = opt.OpticalElement()
        e.loadAtm(atmFile,self.det)
        self.elements.append(e)
    
        #Telescope elements
        self.elements += opt.loadOpticalChain(opticsFile, self.det, lensIP = lensIP, theta=theta)
    
        #Detector Element
        e = opt.OpticalElement()
        e.load("Detector", self.det.bath_temp, 1 - self.det.det_eff)
        self.elements.append(e) 

    
        #Gets HWP index
        try:
            self.hwpIndex = [e.name for e in self.elements].index("HWP")
        except:
            if hwpi:
                self.hwpIndex = hwpi
                e = opt.OpticalElement()
                e.load("HWP", self.elements[hwpi - 1].temp, 0)
#                e.load("HWP", self.elements[hwpi - 1].temp, 0)
                self.elements.insert(hwpi, e)
            else:
                print "ERROR: No HWP specified"
        

        e = opt.OpticalElement()
        e.loadHWP(hwpFile, self.det, self.elements[self.hwpIndex].temp)
        self.elements[self.hwpIndex] = e
        self.dPdT = th.dPdT(self.elements, self.det)
        
        self.propSpectrum()
        self.geta2()
        self.getA2()
        self.geta4()
        self.getA4()
         
        print "HWP Inc", th.powFromSpec(self.freqs, self.UPspecs[self.hwpIndex])
        
    def cumEff(self, index, freq):
        cumEff = 1.
        for i in range(index + 1, len(self.elements)):
            cumEff *= self.elements[i].Eff(freq)
        
        return cumEff
        
        
    def propSpectrum(self):
        N = 400 #subdivision of frequency range
        self.freqs = np.linspace(self.det.flo, self.det.fhi, N) #Frequency array
        self.UPspecs = [np.zeros(N)]  #Unpolarized spectrum before each element
        
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
#    expDir = "../Experiments/small_aperture/LargeTelescope/"
#    atmFile= "Atacama_1000um_60deg.txt"
#    bid = 2
#    opts = {'theta': np.deg2rad(15.0)}
#    tel = Telescope(expDir, atmFile, bid, **opts)
    
    freqRanges = ["LF","MF","HF"]
    
    expDir = "../Experiments/V2_dichroic/45cm/%s_45cm_3waf_silicon/LargeTelescope/"%freqRanges[0]
    atmFile = "Atacama_1000um_60deg.txt"
    bid = 1
    opts = {"hwpi": 10, "lensIP": .0004}
    tel = Telescope(expDir, atmFile, bid, **opts)
    
    print tel.A4 / tel.dPdT