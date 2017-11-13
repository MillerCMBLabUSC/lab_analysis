
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
    def __init__(self, expDir, atmFile,  bandID,  \
                 hwpi = None, lensIP = None, theta = None, writeFile = False,     \
                        printChain = False \
                ):
        
        channelFile = expDir + "channels.txt"
        cameraFile = expDir + "camera.txt"
        opticsFile = expDir + "opticalChain.txt"
        atmFile = "Atacama_1000um_60deg.txt"
        
            
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
            hwpIndex = [e.name for e in self.elements].index("HWP")
        except:
            if hwpi:
                e = opt.OpticalElement()
                e.load("HWP", self.elements[hwpi - 1].temp, 0)
                self.elements.insert(hwpi, e)
            else:
                print "ERROR: No HWP specified"
        
        hwpFile = "../HWP_Mueller/Mueller_AR/Mueller_V2_nu150.0_no3p068_ne3p402_ARcoat_thetain0.0.txt"
        e = opt.OpticalElement()
        e.loadHWP(hwpFile, self.det, self.elements[hwpIndex].temp)
        self.elements[hwpIndex] = e
        print self.det.fbw
        print self.det.flo, self.det.fhi
        
        freqs = np.linspace(self.det.flo, self.det.fhi, 100)
        print np.trapz(map(e.Ip, freqs), freqs) / (freqs[-1] - freqs[0])
        
       
        self.propSpectrum()
        
        
#        print th.powFromSpec(self.freqs , self.UPspecs[3] - self.UPspecs[2])*pW
        
        
#        
    def propSpectrum(self):
        N = 400 #subdivision of frequency range
        self.freqs = np.linspace(self.det.flo, self.det.fhi, N) #Frequency array
        self.UPspecs = [np.zeros(N)]  #Unpolarized spectrum before each element
        
        for (i, el) in enumerate(self.elements):
            
            UPEmitted = th.weightedSpec(self.freqs, el.temp, el.Emis)
            UPTransmitted = self.UPspecs[-1] * map(el.Eff, self.freqs)
            
            self.UPspecs.append(UPEmitted + UPTransmitted)
            
        
        
#        
#           for i in range(len(optElements)):
#        elem = optElements[i]
#        
#        #Unpolarized and polarized spectrum of the element
#        UPEmitted = th.weightedSpec(freqs,elem.temp,elem.Emis)
#        UPTrans = specs[-1] * map(elem.Eff, freqs)
#
#        #Polarized emitted power and IP conversion power
#        PPEmitted = th.weightedSpec(freqs,elem.temp,elem.pEmis)
#
#        
#        ipPower = specs[-1]*map(elem.Ip, freqs) * map(elem.Eff, freqs) 
#        # We don't care about pp created after HWP
#        if i >= hwpIndex:
#            PPEmitted = np.zeros(N)
#            ipPower   = np.zeros(N)
#
#        #Total U/P power introduced by each element
#        UPTotal = UPEmitted - ipPower
#        PPTotal = PPEmitted + ipPower
#        
#        
#        print elem.name, th.powFromSpec(freqs, specs[-1]) * pW, th.powFromSpec(freqs, ipPower) * pW,\
#            th.powFromSpec(freqs, PPEmitted)* pW, th.powFromSpec(freqs, PPTotal) * pW
##        if elem.name == "Window":
##            plt.plot(freqs, PPTotal)
##            plt.plot(freqs, np.ones(len(freqs))* 2 *kB*elem.temp * elem.pEmis(det.band_center))
##            print 2 *kB*elem.temp * elem.pEmis(det.band_center)
##            plt.show()
##            
#
#        # Calculates the total efficiency of everything on detector side of element
#
#        effs = lambda f : map(lambda x : x.Eff(f), optElements[i+1:])
#        peffs = lambda f : map(lambda x : x.pEff(f), optElements[i+1:])
#        if len(effs(det.band_center)) > 0:
#            cumEff = lambda f : reduce((lambda x, y: x*y), effs(f))
#            cumPEff = lambda f : reduce((lambda x, y: x*y), effs(f))
#        else:
#            cumEff = lambda f : 1
#            cumPEff = lambda f : 1
#            
#        print cumPEff(det.band_center)
#            
#            
#            
##            
##        if th.powFromSpec(freqs, PPEmitted)!= 0:
##            abc = th.powFromSpec(freqs, th.weightedSpec(freqs,elem.temp,1))
##            print elem.name, elem.pEmis(det.band_center)*abc * cumPEff(det.band_center)  
##            print elem.name, elem.pEmis(det.band_center)*abc * cumPEff(det.band_center)  / th.dPdT(optElements, det)
#
#        # pEmitTot += abs(th.powFromSpec(freqs, cumPEff(freqs) * PPEmitted))
#        # pIPTot += abs(th.powFromSpec(freqs, cumPEff(freqs) * ipPower))
#
#
#        #Power spectrum seen by the detector coming from this element
#        detUPspec = cumEff(freqs) * UPTotal
#        detPPspec = cumPEff(freqs) * PPTotal
#        
#        # Total Power seen by the detector coming from this element.
#        detUP = abs(.5 * th.powFromSpec(freqs, detUPspec))  # 1/2 because we are goint UP -> PP
#        detPP = abs(th.powFromSpec(freqs, detPPspec))
#        
#        
#        specs.append(UPTotal + UPTrans)
#        UPout.append(detUP)
#        PPout.append(detPP)
#
#        
#        freqs, UPspecs, UPout, PPout = ps.A4Prop(elements, det ,hwpIndex)
#    
#        incPow = map(lambda x : th.powFromSpec(freqs, x), UPspecs)
#    
#        pW_per_Kcmb = th.dPdT(elements, det)*pW
#        effs = [e.Eff(det.band_center) for e in elements[1:]]
#    #    print effs
#        cumEff = reduce(lambda x, y: x * y, effs)
#
#

#
#    #######################################################
#    ## Print table
#    #######################################################
#    outputString +=  "bandID: %d \t freq: %.2f GHz\n"%(det.bid, det.band_center/GHz)
#    outputString +=  "Name\t\t\tIncident UP(pW)\t\tUP Output (pW) \t\tPP Output (pW)\n"
#    outputString +=  "-"*70 + "\n"
#
#    for i in range(len(elements)):
#        outputString +=  "%-8s\t\t%e\t\t%e\t\t%e\n"%(elements[i].name, incPow[i]*pW, UPout[i]*pW, PPout[i]*pW)
#
#    outputString +=  "\n%e pW / Kcmb\n"%pW_per_Kcmb
#    outputString += "Telescope Efficiency: %e"%(cumEff)
#    outputString +=  "\nFinal output up:\t%e pW \t %e Kcmb\n"%(sum(UPout)*pW, sum(UPout)*pW / pW_per_Kcmb)
#    outputString +=  "Final output pp:\t%e pW \t %e Kcmb\n" %(sum(PPout)*pW,  sum(PPout)*pW / pW_per_Kcmb)
#    if printChain:
#        print outputString
#
#    if writeFile:
#        fname = expDir + "%dGHz_opticalPowerTable.txt"%(det.band_center/GHz)
#        f = open(fname, 'w')
#        f.write( outputString)
#        f.close()
#    return det, elements, sum(PPout)*pW, sum(PPout)*pW/pW_per_Kcmb
#
#


if __name__=="__main__":
#     runModel("Experiments/Comparisons/ebex/LargeTelescope/", 1, False) #---    Run Ebex Comparison
    #runModel("Experiments/Comparisons/pb", 1, False) #---    Run PB Comparison

#    det,elements,_,_ = runModel("Experiments/small_aperture/LargeTelescope/", 2, writeFile = False, theta = np.deg2rad(30./2), printChain = True)
    
    expDir = "../Experiments/small_aperture/LargeTelescope/"
    atmFile = "Atacama_1000um_60deg.txt"
    bid = 2
    opts = {'theta': np.deg2rad(15.)}
    tel = Telescope(expDir, atmFile, bid, **opts)
    
#    runModel("Experiments/V2_dichroic/45cm/HF_45cm_3waf_silicon/LargeTelescope/", 1, writeFile = False,  hwpIndex=9 )
#    
#    
#    
#    
#    powEntrance = [[],[]]
#    powerCMB = [[],[]]
#    thetas = [7.5, 10., 12.5, 15.]
#    for theta in map(np.deg2rad, thetas):
#         for i in [1,2]:
#             expDir = "Experiments/small_aperture/LargeTelescope/"
#             
#             det, elements, powAtDetector, powCMB = runModel(expDir, i, writeFile = False, theta = theta, hwpIndex = 9, printChain = False)             
#             
#             telEff =  reduce((lambda x, y : x * y), [e.Eff(det.band_center) for e in elements[2:]])
#             
#             powEntrance[i-1] += [powAtDetector / telEff]
#             powerCMB[i-1] += [powCMB]
#     
#    l = [thetas, powEntrance[0], powEntrance[1], powerCMB[0], powerCMB[1]]
#    print  toTeXTable(np.asarray(l).T)
#    
#    
#     
#        
     
##    
#     powerEntrance = [[],[]]
#     powerCMB = [[],[]]
#     for hwpi in [8, 9]:
#         for i in [1,2]:
#            
#             expDir = "Experiments/small_aperture/LargeTelescope/"
#             expDir = "Experiments/V2_dichroic/45cm/MF_45cm_3waf_silicon/LargeTelescope/"
#            
#             det, elements, powAtDetector, powCMB = runModel(expDir, i, writeFile = False, hwpIndex = hwpi)
##             geta2(elements, det)
#             print det.band_center
#             
#             telEff =  reduce((lambda x, y : x * y), [e.Eff(det.band_center) for e in elements[2:]])
#
#             
#             powerEntrance[hwpi - 8] += [powAtDetector / telEff]
#             powerCMB[hwpi - 8] += [powCMB]
#
#            
            

 #            
 #            print "band_center: %d:"%(band_center)
 #            print "Power at Det: \t %e pW"%(powAtDetector)
 #            print "Power (pW):\t%e pW" % (powAtDetector/ telEff)
 #            print "Power (Kcmb):\t%e"%powCMB
 #            print ""
            
        



    # runAll("Experiments/V2_dichroic/45cm")





    