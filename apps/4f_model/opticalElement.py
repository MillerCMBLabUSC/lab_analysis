import numpy as np


# *****Public variables *****

class OpticalElement:
	def __init__(self, input, bandID=1):
		self.__bid = bandID
		self.name = input[0];
		self.temp = self.__float(input[1])
		self.emis = self.__float(input[6])
		self.spill = self.__float(input[7])
		self.refl = self.__float(input[10])

		if (self.emis=="NA"):
			self.emis = 0
		if (self.spill=="NA"):
			self.spill = 0
		if (self.refl=="NA"):
			self.refl = 0

		self.eff = 1 - self.spill - self.emis - self.refl




	def __float(self, val, unit=1.0):
		try:
			return unit*float(val)
		except:
			try:
				return unit*float(np.array(eval(val))[self.__bid-1])
			except:
				return str(val)










