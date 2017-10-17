import numpy as np
import thermo as th
import matplotlib.pyplot as plt
GHz = 1.e9 # GHz -> Hz
pW = 1.e12 # W -> pW
kB = 1.3806e-23



#Propagates power spectrum of an optical chain
def A4Prop(optElements, det, hwpIndex):

    N = 400 #subdivision of frequency range
    freqs = np.linspace(det.flo, det.fhi, N) #Frequency array
    specs = [np.zeros(N)]  #Unpolarized spectrum before each element

    # pEmitTot = 0
    # pIPTot = 0

    #U/P output powers seen by detector for each element.
    UPout = []
    PPout = []

    for i in range(len(optElements)):
        elem = optElements[i]
        
        #Unpolarized and polarized spectrum of the element
        UPEmitted = th.weightedSpec(freqs,elem.temp,elem.Emis)
        UPTrans = specs[-1] * map(elem.Eff, freqs)

        #Polarized emitted power and IP conversion power
        PPEmitted = th.weightedSpec(freqs,elem.temp,elem.pEmis)

            
        ipPower = specs[-1]*map(elem.Ip, freqs) * map(elem.Eff, freqs) 
        # We don't care about pp created after HWP
        if i >= hwpIndex:
            PPEmitted = np.zeros(N)
            ipPower   = np.zeros(N)

        #Total U/P power introduced by each element
        UPTotal = UPEmitted - ipPower
        PPTotal = PPEmitted + ipPower
        
        
        
#        if elem.name == "Window":
#            plt.plot(freqs, PPTotal)
#            plt.plot(freqs, np.ones(len(freqs))* 2 *kB*elem.temp * elem.pEmis(det.band_center))
#            print 2 *kB*elem.temp * elem.pEmis(det.band_center)
#            plt.show()
#            

        # Calculates the total efficiency of everything on detector side of element

        effs = lambda f : map(lambda x : x.Eff(f), optElements[i+1:])
        peffs = lambda f : map(lambda x : x.pEff(f), optElements[i+1:])
        if len(effs(det.band_center)) > 0:
            cumEff = lambda f : reduce((lambda x, y: x*y), effs(f))
            cumPEff = lambda f : reduce((lambda x, y: x*y), effs(f))
        else:
            cumEff = lambda f : 1
            cumPEff = lambda f : 1
            
            
            
            
        if th.powFromSpec(freqs, PPEmitted)!= 0:
            abc = th.powFromSpec(freqs, th.weightedSpec(freqs,elem.temp,1))
            print elem.name, elem.pEmis(det.band_center)*abc * cumPEff(det.band_center)  
            print elem.name, elem.pEmis(det.band_center)*abc * cumPEff(det.band_center)  / th.dPdT(optElements, det)

        # pEmitTot += abs(th.powFromSpec(freqs, cumPEff(freqs) * PPEmitted))
        # pIPTot += abs(th.powFromSpec(freqs, cumPEff(freqs) * ipPower))


        #Power spectrum seen by the detector coming from this element
        detUPspec = cumEff(freqs) * UPTotal
        detPPspec = cumPEff(freqs) * PPTotal
        
        # Total Power seen by the detector coming from this element.
        detUP = abs(.5 * th.powFromSpec(freqs, detUPspec))  # 1/2 because we are goint UP -> PP
        detPP = abs(th.powFromSpec(freqs, detPPspec))
        
        
        specs.append(UPTotal + UPTrans)
        UPout.append(detUP)
        PPout.append(detPP)



    return freqs, specs, UPout, PPout