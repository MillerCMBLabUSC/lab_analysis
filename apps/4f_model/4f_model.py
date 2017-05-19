import numpy as np
import thermo as th

class OpticalElement:
	def __init__(self, name, temp,emis,eff):
		self.name = name
		self.temp = temp
		self.emis = emis
		self.eff = eff

def __float(val, bid = None, unit=1.0):
	try:
		return unit*float(val)
	except:
		try:
			return unit*float(np.array(eval(val))[bid-1])
		except:
			return 0



#########################################################
#   Input Data
#########################################################
expDir = "Experiments/MF_30cm_silicon/"
channelFile = expDir + "channels.txt"
cameraFile = expDir + "camera.txt"
opticsFile = expDir + "opticalChain.txt"
atmFile = "Atacama_1000um_60deg.txt"
# Must be 1 or 2. This determines the frequency and is needed to import the proper absorption
bandID = 2

# Gets channel frequency bounds
GHz = 1.e9 # GHz -> Hz

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
elements.append(OpticalElement("CMB", 2.725, 1, 1))


#Calculation of atmosphere efficiency
fs, ts = np.loadtxt(atmFile, dtype=np.float, unpack=True, usecols=[0, 3]) #frequency/efficiency pairs from input file
fs*=GHz # [Hz]

freqs = []
effs = []
for i in range(len(fs)):
	if fs[i] > flo and fs[i] < fhi:
		freqs.append(fs[i])
		effs.append(ts[i])
## The total transmission coeff is the average of coefficients over the frequency range.
eff = np.trapz(effs, freqs)/(freqs[-1] - freqs[0])
emis = 1-eff

#Atmosphere optical element
elements.append(OpticalElement("Atm", 273., emis, eff))



#########################################################
#   Load Optical Elements
#########################################################
opt_string = np.loadtxt(opticsFile, dtype = np.str,usecols=[0,1,6,7,10])
# print opt_string
for i in range(1, len(opt_string)):
	name = opt_string[i][0]
	temp = __float(opt_string[i][1])
	if name =="Aperture":
		eff = th.spillEff(pixSize, f_num, waistFact, band_center)
		absorb = 1 - eff
		spill = 0
		refl = 0
	else:
		absorb = __float(opt_string[i][2], bandID)
		spill = __float(opt_string[i][3])
		refl = __float(opt_string[i][4])
		eff = 1 - absorb - spill- refl
	
	elements.append(OpticalElement(name, temp, absorb, eff))


## Detector element
#
elements.append(OpticalElement("Detector", .1, 1 - det_eff, det_eff))



#########################################################
#   Calculate incident power on each element
#########################################################
incPowers = [0]
outPowers = []

for i in range(len(elements)):
	p = th.bbPower(elements[i].temp, elements[i].emis,flo,fhi)
	#Blackbody power output
	outPowers.append(p)
	# Total power output == (bb Pow) + (incidentPow) * (Efficiency)
	incPowers.append(incPowers[-1]*elements[i].eff + p)


#########################################################
#   Print table
#########################################################
print "freq: %.2f GHz"%(band_center/GHz)
print "Name\t\t\tOutput power(W)\t\tIncident power(W)"
print "-"*50

for i in range(len(elements)):
	print "%-8s\t\t%e\t\t%e"%(elements[i].name, outPowers[i],incPowers[i])

print "\nFinal output power:\t%e W"%incPowers[-1]
	