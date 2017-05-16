import numpy as np
import scipy.integrate as intg

# *****Public variables *****
#Physical Constants
#Everything is in MKS units
#Planck constant [J/s]
h = 6.6261e-34
#Boltzmann constant [J/K]
kB = 1.3806e-23
#Speed of light [m/s]
c = 299792458.0
#Pi
PI = 3.14159265

class OpticalElement:
	def __init__(self, input, f1, f2, bandID=1):
		self.__bid = bandID
		self.name = input[0];
		self.temp = self.__float(input[1])
		self.emis = self.__float(input[6])
		self.spill = self.__float(input[7])
		self.refl = self.__float(input[10])

		self.freq1=f1
		self.freq2=f2

		if (self.emis=="NA"):
			self.emis = 0
		if (self.spill=="NA"):
			self.spill = 0
		if (self.refl=="NA"):
			self.refl = 0

		self.eff = 1 - self.spill - self.emis - self.refl

		self.__bbPower()




	def __float(self, val, unit=1.0):
		try:
			return unit*float(val)
		except:
			try:
				return unit*float(np.array(eval(val))[self.__bid-1])
			except:
				return str(val)


	#Calculates total black body power for each element.
	def __weightedSpec(self, freq):
		occ = 1.0/(np.exp(h*freq/(self.temp*kB)) - 1)
		AOmega = (c/freq)**2
		return (AOmega*(2*self.emis*h*freq**3)/(c**2)* occ)


	def __bbPower(self):
		self.power = .5*intg.quad(self.__weightedSpec, self.freq1, self.freq2)[0]







