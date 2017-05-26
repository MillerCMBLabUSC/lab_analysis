import numpy as np
import thermo as th

class OpticalElement:
	def __init__(self, name, temp,emis,eff, ip = 0, pEmis = 0, pEff = None):
		self.name = name
		self.temp = temp

		#Emissions can be either constants or functions of frequency
		self.emis = emis  # Unpolarized emission
		self.pEmis = pEmis # Polarized emission

		self.eff = eff #Efficiency
		self.pEff = (eff if pEff == None else pEff) #Polarized efficiency
		self.ip = ip #IP coefficient
		
def __float(val, bid = None, unit=1.0):
	try:
		return unit*float(val)
	except:
		try:
			return unit*float(np.array(eval(val))[bid-1])
		except:
			return 0



def loadOpticalChain(opticsFile,bandID, band_center,fbw, pixSize, f_num, waistFact):
	flo = band_center*(1 - .5 * fbw) #detector lower bound [Hz]
	fhi = band_center*(1 + .5 * fbw) #detector upper bound [Hz]

	elements = []
	opt_string = np.loadtxt(opticsFile, dtype = np.str,usecols=[0,1,6,7,8,10])
	# print opt_string

	chi1 = np.deg2rad(25.7312) #Average primary mirror incident angle
	chi2 = np.deg2rad(19.5982) #Average secondary mirror incident angle

	lensIP = .0004

	for i in range(1, len(opt_string)):
		if i == 2:
			continue
		name = opt_string[i][0]
		temp = __float(opt_string[i][1])
		if name =="Aperture":
			eff = th.spillEff(pixSize, f_num, waistFact, band_center)
			absorb = 1 - eff
			spill = 0
			spillTemp = 0
			refl = 0
		else:
			absorb = __float(opt_string[i][2], bandID)
			spill = __float(opt_string[i][3])
			spillTemp = __float(opt_string[i][4])
			refl = __float(opt_string[i][5])
			eff = 1 - absorb - spill- refl

		## Adds spill and scatter effects to the emission
		emis = absorb + spill * th.powFrac(spillTemp, temp, flo, fhi)
		elements.append(OpticalElement(name, temp,  emis  , eff))

		if name == "Lens":
			elements[-1].ip = lensIP


	# Sets polarized emis of primary mirror
	elements[0].pEmis = (lambda x : -th.getLambdaOpt(x, chi1))
	elements[0].ip =    (lambda x : -th.getLambdaOpt(x, chi1))

	# Sets polarized emis of secondary mirror
	elements[1].pEmis = (lambda x : -th.getLambdaOpt(x, chi2))
	elements[1].ip =    (lambda x : -th.getLambdaOpt(x, chi2))

	return elements
