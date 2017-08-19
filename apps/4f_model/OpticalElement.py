import numpy as np
import thermo as th
from scipy import interpolate
from scipy import integrate as intg
import Detector as dt


# Units and Constants
GHz = 1.e9 # GHz -> Hz
pW = 1.e12 # W -> pW



#Vacuum Permitivity
eps0 = 8.85e-12
#Resistivity of the mirror
rho=2.417e-8




class OpticalElement:

	# Loads an optical element from name, temp, and absorption
	def load(self, name, temp, absorb):
		self.name = name
		self.temp = temp
		self.absorb = absorb
		self.spill = 0
		self.refl = 0
		self.ipVal = None
	# Loads an optical element from an atmosphere file
	def loadAtm(self, atmFile, det):
		freqs, temps, trans = np.loadtxt(atmFile, dtype=np.float, unpack=True, usecols=[0, 2, 3]) #frequency/efficiency pairs from input file
		freqs*=GHz # [Hz]

		#Reads Rayleigh Jeans temperature from file and takes average
		tempF = interpolate.interp1d(freqs, temps, kind = "linear")
		x = np.linspace(det.flo, det.fhi, 400)
		y = tempF(x)

		self.temp = intg.simps(y, x=x)/(det.fhi - det.flo)
		self.name = "Atm"
		self.fs = freqs
		self.ts = trans
		self.ipVal = None

	#Loads an optical element from 
	def loadParams(self, params, det, chi = None, ipVal = None):
		#Detector Parameters
		self.det = det

		#Gets params from dictionary
		self.name = params["Element"]
		self.thick = self._toFloat(params["Thick"])
		self.index = self._toFloat(params["Index"])
		self.lossTan = self._toFloat(params["LossTan"])
		self.temp = self._toFloat(params["Temp"])
		self.absorb = self._toFloat(params["Absorb"], self.det.bid)
		self.spill = self._toFloat(params["Spill"])
		self.spillTemp = self._toFloat(params["SpillTemp"])
		self.refl = self._toFloat(params["Refl"])
		self.scattFrac = self._toFloat(params["ScattFrac"])
		self.scattTemp = self._toFloat(params["ScattTemp"])

		# Parameters not included in opticalChain file
		self.ipVal = ipVal
		self.chi = chi

	#Get element Ip 
	def Ip(self, freq):
		if self.name == "Mirror":
			if self.chi == None:
				print "Incidence angle Chi must be defined for mirrors"
				return 

			geom = (1 / np.cos(self.chi) - np.cos(self.chi))
			return 2 * geom * np.sqrt(4 * np.pi * eps0 * rho * freq)

		elif self.name == "Lens":
			if self.ipVal == None:
				print "IP values must be defined for lenses"
				return

			return self.ipVal

		if self.ipVal:
			return self.ipVal
		return 0

	def Eff(self, freq):
		if self.name == "Atm":
			return np.interp(freq,self.fs,self.ts) 
		elif self.name == "Aperture":
			return th.spillEff(self.det.pixSize, self.det.f_num, self.det.waistFact, self.det.band_center)
		else:
			if self.absorb == 0 and self.lossTan != 0:
				ab = self.Emis( freq)
			else:
				ab = self.absorb
			return  1 - ab - self.spill- self.refl

	def pEff(self, freq):
		return self.Eff(freq)


	def Emis(self, freq):
		if self.name == "Atm":
			# Returns 1 because we are using Rayleigh Jeans temperature
			return 1
		if self.name == "Aperture":
			return (1 - self.Eff(freq) + self.spill * th.powFrac(self.spillTemp, self.temp, self.det.flo, self.det.fhi))
		else:
			if self.spill != 0:
				return self.absorb + self.spill * th.powFrac(self.spillTemp, self.temp, self.det.flo, self.det.fhi)
				
			else:
				# if self.absorb == 0 and self.lossTan != 0:
				# 	return th.dielectricLoss(self.lossTan, self.thick, self.index, self.det.band_center)
				return self.absorb



	def pEmis(self, freq):
		return -self.Ip(freq)


	def _toFloat(self, val, bid= None, unit=1.0):
		if val == "NA":
			return 0
		else:
			v = eval(val)
			if type(v) == float:
				return v * unit
			if type(v) == list:
				return v[bid-1] * unit





def loadOpticalChain(opticsFile,det, lensIP = .0004):
	data = np.loadtxt(opticsFile, dtype=np.str)
	keys = data[0]

	alumFip = .000138
	windowIP = .000014

	
	chi = map(np.deg2rad, [25.7312, 19.5982])	

	mirrorNum = 0

	elements = []
	for line in data[1:]:
		params = dict(zip(keys, line))
		e = OpticalElement()

		if params["Element"] == "Mirror":
			if mirrorNum >= 2:
				continue
			e.loadParams(params, det, chi = chi[mirrorNum])
			mirrorNum += 1

		elif params["Element"] == "Lens":
			e.loadParams(params, det, ipVal = lensIP)
		elif params["Element"] == "AluminaF":
			e.loadParams(params, det, ipVal = alumFip)
		elif params["Element"] == "Window":
			e.loadParams(params, det, ipVal = windowIP)
		else:
			e.loadParams(params, det)



		elements.append(e)

	return elements




