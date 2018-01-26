import matplotlib.pyplot as plt
import matplotlib.pyplot as plt

mport numpy as np
from lab_analysis.libs.noise import simulate
import sys


alpha = 1.0
white_noise_sigma = 1.0
f_knee = 2.0
sample_rate = 100.0

class Correlate:

	def __init__(self,inputlength):
		self.copies = []
		self.correlation = None
		self.orig = inputlength
	def fcorrelate(self, correlations):
		"""This function correlates a 1/f timestream forward in time by 1 second"""


		self.correlation = 'Foward' # set correlation

		#first create a sample that is the union of all correlated samples, then we will take frames of length_ts, each shifted by 1 second
		sample = (simulate.simulate_noise(alpha,white_noise_sigma,self.orig + correlations + 1,f_knee,sample_rate))
		for i in range(0,correlations):
			self.copies.append(sample[i:i+self.orig])

		#flatten the list of lists
		self.copies = [item for sublist in self.copies for item in sublist]


	def bcorrelate(self, correlations):
		"""This function correlates a 1/f time stream backward in time by 1 second"""


		self.correlation = 'Backward' #set correlation

		#first create a sample that is a union of all correlated samples, then we will take frames of lenght_ts, each shifted by one second
		sample = (simulate.simulate_noise(alpha,white_noise_sigma,self.orig + correlations,f_knee,sample_rate))
		for i in range(0,correlations):
			self.copies.append(self.copies[0][-(i+self.orig):-i])

		#flatten the lists of lists
		self.copies = [item for sublist in self.copies for item in sublist]





