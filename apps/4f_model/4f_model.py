import numpy as np
import thermo as th
import OpticalElement as opt


#########################################################
#   Input Data 											
#########################################################
expDir = "Experiments/MF_30cm_silicon/LargeTelescope/"
channelFile = expDir + "channels.txt"
cameraFile = expDir + "camera.txt"
opticsFile = expDir + "opticalChain.txt"
atmFile = "Atacama_1000um_60deg.txt"
# Must be 1 or 2. This determines the frequency and is needed to import the proper absorption


# Gets channel frequency bounds
GHz = 1.e9 # GHz -> Hz
pW = 1.e12 # W -> pW

bandID = 1

ch_str = np.loadtxt(channelFile, dtype=np.str)
band_center = float(ch_str[bandID][2])*GHz #[Hz]
fbw = float(ch_str[bandID][3]) #fractional bandwidth
pixSize = float(ch_str[bandID][4])/1000.
waistFact = float(ch_str[bandID][6])
det_eff = float(ch_str[bandID][7])


flo = band_center*(1 - .5 * fbw) #detector lower bound [Hz]
fhi = band_center*(1 + .5 * fbw) #detector upper bound [Hz]

##Import camera data
cam_str = np.loadtxt(cameraFile, dtype=np.str, usecols=[2])
f_num = float(cam_str[2])
bath_temp = float(cam_str[2])


elements = [] #List of optical elements

#CMB optical element
elements.append(opt.OpticalElement("CMB", 2.725, 1, 1))


#Calculation of atmosphere efficiency
fs, ts = np.loadtxt(atmFile, dtype=np.float, unpack=True, usecols=[0, 3]) #frequency/efficiency pairs from input file
fs*=GHz # [Hz]

elements.append(opt.OpticalElement("Atm", 273., 0, 0))
elements[-1].eff = lambda x :  np.interp(x,fs,ts) 
elements[-1].emis = lambda x : 1 -  np.interp(x,fs,ts) 



#########################################################
#   Load Optical Elements
#########################################################
elements += opt.loadOpticalChain(opticsFile, bandID, band_center,fbw,pixSize, f_num, waistFact)


hwpIndex = 11
elements.insert(hwpIndex, opt.OpticalElement("HWP", elements[hwpIndex - 1].temp, 0, 1))

## Detector element
elements.append(opt.OpticalElement("Detector", .1, 1 - det_eff, det_eff))


#########################################################
#   Calculate incident power on each element
#########################################################
incPowers = []
outPowers = []

N=200
freqs = np.linspace(flo, fhi, N) #Frequency array
UPspecs = [np.zeros(N)]  #Unpolarized spectrum before each element
PPspecs = [np.zeros(N)] #Polarized spectrum before each element

# We want to propagate the spectrum from element to element
for i in range(len(elements)):
	elem = elements[i]
	#Black body spectrum of the current element
	elemUPSpec = th.weightedSpec(freqs,elem.temp,elem.emis)
	elemPPSpec = th.weightedSpec(freqs,elem.temp,elem.pEmis)

	if callable(elem.eff):
		upEff = map(elem.eff, freqs)
	else:
		upEff = elem.eff

	if callable(elem.pEff):
		ppEff = map(elem.pEff, freqs)
	else:
		ppEff = elem.pEff
	if callable(elem.ip):
		ip = map(elem.ip, freqs)
	else:
		ip = np.full(N,elem.ip)


	if (i < hwpIndex):
		ups = UPspecs[-1] * upEff * map(lambda x : 1 - x, ip)  + elemUPSpec
		pps = PPspecs[-1]*ppEff + UPspecs[-1]*ip + elemPPSpec 
	else:
		ups = UPspecs[-1]*upEff  + elemUPSpec
		pps = PPspecs[-1]*ppEff 

	# ups = UPspecs[-1]*upEff  + elemUPSpec
	# pps = PPspecs[-1]*ppEff 

	UPspecs.append(ups)
	PPspecs.append(pps)
	outPowers.append(.5 * np.trapz(elemUPSpec, freqs))

incUP = map(lambda x : .5*np.trapz(x, freqs), UPspecs)
incPP = map(lambda x : .5*np.trapz(x, freqs), PPspecs)


#########################################################
#   Print table
#########################################################
print "bandID: %d \t freq: %.2f GHz"%(bandID, band_center/GHz)
print "Name\t\t\tOutput power(pW)\tIncident UP (pW) \tIncident PP (pW)"
print "-"*70

for i in range(len(elements)):
	print "%-8s\t\t%e\t\t%e\t\t%e"%(elements[i].name, outPowers[i]*pW, incUP[i]*pW, incPP[i]*pW)

print "\nFinal output up:\t%e pW"%(incUP[-1]*pW)
print "Final output pp:\t%e pW"%(incPP[-1]*pW)











	