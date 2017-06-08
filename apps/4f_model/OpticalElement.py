import numpy as np
import thermo as th



# Units and Constants
GHz = 1.e9 # GHz -> Hz
pW = 1.e12 # W -> pW

def _toFunc(f):
	if callable(f):
		return f
	else:
		return (lambda x : f)

class OpticalElement:
	def __init__(self, name, temp,emis,eff, ip = 0, pEmis = 0, pEff = None):
		self.name = name
		self.temp = temp

		#Emissions can be either constants or functions of frequency

		self.emis = _toFunc(emis)
		self.pEmis = _toFunc(pEmis)
		self.eff = _toFunc(eff) #Efficiency
		self.pEff = (self.eff if pEff == None else _toFunc(pEff)) #Polarized efficiency
		self.ip = _toFunc(ip) #IP coefficient
		
def __float(val, bid = None, unit=1.0):
	try:
		return unit*float(val)
	except:
		try:
			return unit*float(np.array(eval(val))[bid-1])
		except:
			return 0


def loadAtm(atmFile):

	fs, ts = np.loadtxt(atmFile, dtype=np.float, unpack=True, usecols=[0, 3]) #frequency/efficiency pairs from input file
	fs*=GHz # [Hz]

	e = OpticalElement("Atm", 273., .0, 0)
	e.eff = lambda x :  np.interp(x,fs,ts) 
	e.emis = lambda x : 1 -  np.interp(x,fs,ts) 

	return e



def loadOpticalChain(opticsFile,det):

	elements = []
	opt_string = np.loadtxt(opticsFile, dtype = np.str,usecols=[0,1,6,7,8,10])
	# print opt_string

	chi = map(np.deg2rad, [25.7312, 19.5982])

	lensIP = .0004
	# lensIP = .00005
	
	mirrorNum = 0

	#### For Ebex:
	# flensIP = [.017, .02]
	# chi = map(np.deg2rad, [31.299, 20.299])

	#For Polarbear
	# chi = [np.deg2rad(32.5)]


	for i in range(1, len(opt_string)):
		
		name = opt_string[i][0]
		temp = __float(opt_string[i][1])

		if name == "Mirror" and mirrorNum >= 2:
			continue

		if name =="Aperture":
			eff = th.spillEff(det.pixSize, det.f_num, det.waistFact, det.band_center)
			absorb = 1 - eff
			spill = 0
			spillTemp = 0
			refl = 0
		else:
			absorb = __float(opt_string[i][2], det.bid)
			spill = __float(opt_string[i][3])
			spillTemp = __float(opt_string[i][4])
			refl = __float(opt_string[i][5])
			eff = 1 - absorb - spill- refl

		## Adds spill and scatter effects to the emission
		emis = absorb + spill * th.powFrac(spillTemp, temp, det.flo, det.fhi)
		elements.append(OpticalElement(name, temp,  emis  , eff))


		#Edits can be made in specific cases once the element is created
		if name == "Mirror" and mirrorNum < len(chi):
			c = chi[mirrorNum]
			
			elements[-1].pEmis = (lambda x : th.getLambdaOpt(x, c))
			elements[-1].ip =    (lambda x : -th.getLambdaOpt(x, c))
			mirrorNum += 1

		if name == "Lens":
			elements[-1].ip = _toFunc(lensIP)

		if name=="FieldLens":
			elements[-1].ip = _toFunc(flensIP[det.bid - 1])



	return elements
