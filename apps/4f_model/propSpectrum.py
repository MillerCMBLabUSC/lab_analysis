import numpy as np
import thermo as th


#Propagates power spectrum of an optical chain
def propSpec(optElements, det, hwpIndex):

	N = 400 #subdivision of frequency range
	freqs = np.linspace(det.flo, det.fhi, N) #Frequency array
	UPspecs = [np.zeros(N)]  #Unpolarized spectrum before each element
	PPspecs = [np.zeros(N)] #Polarized spectrum before each element

	outPowers = []

	for i in range(len(optElements)):
		elem = optElements[i]

		#Unpolarized and polarized spectrum of the element
		elemUPSpec = th.weightedSpec(freqs,elem.temp,elem.emis)
		elemPPSpec = th.weightedSpec(freqs,elem.temp,elem.pEmis)


		upEff = map(elem.eff, freqs) #Unpolarized efficiency of element for each frequency
		ppEff = map(elem.pEff, freqs) # Polarized efficiency for each frequency
		ip =    map(elem.ip, freqs) #IP for each frequency

		if (i < hwpIndex):
			ups = UPspecs[-1] * upEff * map(lambda x : 1 - x, ip)  + elemUPSpec
			pps = PPspecs[-1]*ppEff + UPspecs[-1]*ip + elemPPSpec 
		else:
			ups = UPspecs[-1]*upEff  + elemUPSpec
			pps = PPspecs[-1]*ppEff 


		UPspecs.append(ups)
		PPspecs.append(pps)
		outPowers.append(.5 * np.trapz(elemUPSpec, freqs))

	return freqs, UPspecs, PPspecs, outPowers