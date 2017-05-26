import numpy as np
import thermo as th
import OpticalElement as opt
import Detector as dt

#########################################################
#   Input Data 											
#########################################################
expDir = "Experiments/MF_30cm_silicon/LargeTelescope/"
channelFile = expDir + "channels.txt"
cameraFile = expDir + "camera.txt"
opticsFile = expDir + "opticalChain.txt"
atmFile = "Atacama_1000um_60deg.txt"

# Must be 1 or 2. This determines the frequency and is needed to import the proper absorption
bandID = 1


# Units and Constants
GHz = 1.e9 # GHz -> Hz
pW = 1.e12 # W -> pW

#Imports detector data 
det = dt.Detector(channelFile, cameraFile, bandID)


##################################################################################################################
#   Loads Optical Elements
##################################################################################################################

elements = [] #List of optical elements

#CMB optical element
elements.append(opt.OpticalElement("CMB", 2.725, 1, 1))


#Atmosphere optical element
fs, ts = np.loadtxt(atmFile, dtype=np.float, unpack=True, usecols=[0, 3]) #frequency/efficiency pairs from input file
fs*=GHz # [Hz]

elements.append(opt.OpticalElement("Atm", 273., 0, 0))
elements[-1].eff = lambda x :  np.interp(x,fs,ts) 
elements[-1].emis = lambda x : 1 -  np.interp(x,fs,ts) 

# Loads elements from Optical Chain file
elements += opt.loadOpticalChain(opticsFile, det)

#Inserts HWP at desired position
hwpIndex = 11
elements.insert(hwpIndex, opt.OpticalElement("HWP", elements[hwpIndex - 1].temp, 0, 1))


## Detector element
elements.append(opt.OpticalElement("Detector", .1, 1 - det.det_eff, det.det_eff))


#########################################################
#   Calculate incident power on each element
#########################################################
incPowers = []
outPowers = []

N=200
freqs = np.linspace(det.flo, det.fhi, N) #Frequency array
UPspecs = [np.zeros(N)]  #Unpolarized spectrum before each element
PPspecs = [np.zeros(N)] #Polarized spectrum before each element

# We want to propagate the spectrum from element to element
for i in range(len(elements)):
	elem = elements[i]


	#Black body spectrum of the current element
	elemUPSpec = th.weightedSpec(freqs,elem.temp,elem.emis)
	elemPPSpec = th.weightedSpec(freqs,elem.temp,elem.pEmis)

	upEff = map(elem.eff, freqs)
	ppEff = map(elem.pEff, freqs)
	ip =    map(elem.ip, freqs)

	if (i < hwpIndex):
		ups = UPspecs[-1] * upEff * map(lambda x : 1 - x, ip)  + elemUPSpec
		pps = PPspecs[-1]*ppEff + UPspecs[-1]*ip + elemPPSpec 
	else:
		ups = UPspecs[-1]*upEff  + elemUPSpec
		pps = PPspecs[-1]*ppEff 


	UPspecs.append(ups)
	PPspecs.append(pps)
	outPowers.append(.5 * np.trapz(elemUPSpec, freqs))

incUP = map(lambda x : th.powFromSpec(freqs, x), UPspecs)
incPP = map(lambda x : th.powFromSpec(freqs, x), PPspecs)


#########################################################
#   Print table
#########################################################
print "bandID: %d \t freq: %.2f GHz"%(det.bid, det.band_center/GHz)
print "Name\t\t\tOutput power(pW)\tIncident UP (pW) \tIncident PP (pW)"
print "-"*70

for i in range(len(elements)):
	print "%-8s\t\t%e\t\t%e\t\t%e"%(elements[i].name, outPowers[i]*pW, incUP[i]*pW, incPP[i]*pW)

print "\nFinal output up:\t%e pW"%(incUP[-1]*pW)
print "Final output pp:\t%e pW"%(incPP[-1]*pW)











	